"""
This file includes the app routes.
"""
import os.path
import time
from datetime import datetime, timezone, timedelta
from json import dumps
from logging import debug
from os import getenv, urandom, remove
from typing import Tuple, Union
from flask_cors import CORS
from flask import Flask, g, request, jsonify, send_from_directory, Response, send_file
from flask_jwt_extended import JWTManager, jwt_required, current_user, create_access_token, set_access_cookies, \
    unset_jwt_cookies, get_jwt_identity, get_jwt
from dataclasses import asdict

from werkzeug.utils import secure_filename

from mbsbackend.datatypes.classes import User_, Student, Advisor, Proposal, get_user, Recommended, Instructor, \
    convert_department, Thesis, Has, DBR, Jury
from mbsbackend.external_services.plagiarism_api import PlagiarismManager
from mbsbackend.server_internals.authentication import authenticate, identity
from mbsbackend.server_internals.consants import forbidden_fields, version_number
from mbsbackend.server_internals.verification import returns_json, full_json, requires_json


def create_app() -> Flask:
    """
    This is a typical use of the create app function in flask.
        although I recognise this looks complex, it is not a
        typical function.
    """
    app = Flask(__name__)  # Create the app object.
    jwt = JWTManager(app)
    plagiarism_api = PlagiarismManager()
    CORS(app,  supports_credentials=True)
    app.config["SECRET_KEY"] = getenv("FLASK_SECRET_KEY", urandom(24))
    app.config['JWT_AUTH_URL_RULE'] = '/jwt'
    app.config['DEBUG'] = False
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    @app.route('/')
    def test_url():
        return f"Server up! {version_number}.", 200

    @jwt.user_lookup_loader
    def curr_user(header, payload) -> User_:
        return User_.fetch(payload['sub']['user_id'])

    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            expire_timestamp = get_jwt()['exp']
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > expire_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except(RuntimeError, KeyError):
            return response

    @app.route('/jwt', methods=['POST'])
    def login():
        """
        Login the user to the MBS.

        :return the JWT access token if successful with status
            code 201. Otherwise return error message with status
            code 401.
        """
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        if authenticate(username, password):
            user_id = User_.fetch_where('email', username)[0]
            access_token = create_access_token(identity=user_id)
            response = jsonify(access_token=access_token)
            set_access_cookies(response, access_token)
            return response, 201
        return "", 401

    @app.route('/jwt', methods=['DELETE'])
    @jwt_required()
    def logout():
        """
        Logout the user from the system.

        :return The response which invalidates the token as
            well as 204 status code.
        """
        response = jsonify({'msg': 'logout successful'})
        unset_jwt_cookies(response)
        return response, 204

    @app.route('/users', methods=["GET"])
    @returns_json
    @jwt_required()
    def get_user_information() -> Tuple[dict, int]:
        """
        Get information about the currently logged in user.

        :return information about the user.
        """
        user: User_ = User_.fetch(current_user.user_id)
        user = user.downcast()  # Downcast the user.
        user_info = {}
        if isinstance(user, Student) and user.advisor:
            user_info['role'] = 'student'  # Set the role.
            user_info['student'] = asdict(user)
            user_info['username'] = user_info['student']['name_']  # Remove in Production. Backward Compatibility.
            user_info['student']['latest_thesis_id'] = user.latest_thesis_id
            user_info['advisor'] = asdict(user.advisor)
        elif isinstance(user, Student) and not user.advisor:
            user_info['role'] = 'student'
            user_info['student'] = asdict(user)
            user_info['student']['latest_thesis_id'] = user.latest_thesis_id
            user_info['username'] = user_info['student']['name_']  # Remove in Production. Backward Compatibility.
            user_info['username'] = user.name_
        elif isinstance(user, Advisor):
            user_info['role'] = 'advisor'
            user_info['advisor'] = asdict(user)
            user_info['username'] = user_info['advisor']['name_']  # Remove in Production. Backward Compatibility.
        elif isinstance(user, DBR):
            user_info['role'] = 'DBR'
            user_info['DBR'] = asdict(user)
            user_info['username'] = user_info['DBR']['name_']
        elif isinstance(user, Jury):
            user_info['role'] = 'jury'
            user_info['jury'] = asdict(user)
            user_info['username'] = user_info['jury']['name_']
        else:
            return {"message": "Invalid user type"}, 400
        for key in user_info:
            if isinstance(user_info[key], dict):
                del user_info[key]['password']  # We shouldn't passwords
                convert_department(user_info[key])  # And we should send dept names rather than ids.
        return user_info, 200

    @app.route('/students/<student_id>', methods=["GET"])
    @returns_json
    @jwt_required()
    def get_student_information(student_id: str) -> Tuple[dict, int]:
        """
        Get user information of a specific student.
        """
        student = get_user(Student, int(student_id))
        if student is None:
            return {'msg': 'Student not found.'}, 400
        return student, 200

    @app.route('/students/<student_id>', methods=["PATCH"])
    @full_json()
    @jwt_required()
    def update_student_information(student_id: str) -> Tuple[dict, int]:
        """
        Update information on a student, given that the student is the
            current user.

        TODO: In the future, this endpoint will support advisor doing changes.
        """
        user = current_user.downcast()
        id_ = int(student_id)
        if not isinstance(user, Student) and user.student_id != student_id:
            return {"msg": "Unauthorised"}, 401
        payload = request.json
        acceptable_fields = [field for field in payload if
                             field not in forbidden_fields["Student"] and field in Student.__dataclass_fields__]
        for field in acceptable_fields:
            setattr(user, field, payload[field])  # Update the field of the user.
        user.update()  # Update it in the database.
        return get_user(Student, user.user_id), 200

    @app.route('/advisors/<advisor_id>', methods=["GET"])
    @returns_json
    @jwt_required()
    def get_advisor_information(advisor_id: str) -> Tuple[dict, int]:
        """
        Get user information about a specific advisor.
        """
        advisor = get_user(Advisor, int(advisor_id))
        if advisor is None:
            return {"msg": 'Advisor not found.'}, 400
        return advisor, 200

    @app.route('/recommendations', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_recommendations() -> Tuple[Union[list, dict], int]:
        """
        Get the recommendations (advisor recommendations) for
            the currently logged in Student user.
        """
        student = current_user.downcast()
        if not isinstance(student, Student):
            return {"msg": "Only the student may have recommendations"}, 403
        elif student.has_proposed:
            return {"msg": "Already proposed to an advisor"}, 409
        recommendations = student.recommendations
        if not recommendations:
            return {"msg": "No recommended advisors found."}, 404
        # If there are recommendations, convert them to dictionaries and return them as JSON.
        return [asdict(recommendation) for recommendation in recommendations], 200

    @app.route('/proposals', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_proposals() -> Tuple[Union[dict, list], int]:
        """
        Get a list of proposals made to this Advisor user
            that is currently logged in.
        """
        advisor = current_user.downcast()
        if not isinstance(advisor, Advisor):  # If the current user is not an advisor.
            return {"msg": "Only the advisors can see their proposals."}, 403
        proposals = advisor.proposals
        return [asdict(proposal) for proposal in proposals], 200

    @app.route('/proposals/<proposal_id>', methods=['DELETE'])
    @returns_json
    @jwt_required()
    def reject_proposal(proposal_id: str) -> Tuple[dict, int]:
        """
        Reject a proposal by deleting it from the
            database. This also turns the student's
            has_proposed into false.
        """
        advisor = current_user.downcast()
        if not isinstance(advisor, Advisor):  # If the current user is not an advisor.
            return {"msg": "Only the advisors can see their proposals."}, 403
        proposal = Proposal.has(proposal_id) and Proposal.fetch(proposal_id)
        if not proposal:
            return {"msg": "Proposal deleted."}, 204  # Since DELETE is idempotent, this is alright.
        if not proposal.advisor_id == advisor.advisor_id:
            return {"msg": "You aren't authorised for this."}, 401
        proposal.delete()
        student = Student.fetch(proposal.student_id)
        student.has_proposed = False
        student.update()
        return {"msg": "Proposal deleted."}, 204

    @app.route('/proposals', methods=["POST"])
    @full_json(required_keys=('advisor_id', ))
    @jwt_required()
    def create_new_proposal() -> Tuple[dict, int]:
        """
        A student user may create a proposal to an advisor
            user, provided that they're in their recommended list of
            advisors.
        """
        payload = request.json
        student = current_user.downcast()
        if not isinstance(student, Student):
            return {"msg": "Unauthorised."}, 403
        advisor_id = payload["advisor_id"]
        student_recommended_advisors = [recommendation.advisor_id for recommendation in student.recommendations]
        if student.has_proposed:
            return {"msg": "Already proposed."}, 409
        elif student.thesis_topic is None or student.thesis_topic == "NULL":
            return {"msg": "Cannot propose to a student without having a valid thesis topic."}, 409
        elif advisor_id not in student_recommended_advisors:  # If this student was not recommended their advisor.
            return {"msg": "Advisor is not recommended to the user."}, 409
        elif not Advisor.has(advisor_id):
            return {"msg": "No such advisor."}, 404
        else:  # Otherwise we are fine and can propose.
            student.has_proposed = True
            student.update()
            proposal_ = Proposal(-1, student.student_id, advisor_id)
            proposal_.create()
            return asdict(proposal_), 201

    @app.route('/proposals/<proposal_id>', methods=["PUT"])
    @returns_json
    @jwt_required()
    def approve_proposal(proposal_id: str) -> Tuple[dict, int]:
        """
        An advisor user can approve the proposals made to them.
        """
        advisor = current_user.downcast()
        if not isinstance(advisor, Advisor):
            return {"msg": "Unauthorised."}, 403
        proposal = Proposal.has(int(proposal_id)) and Proposal.fetch(int(proposal_id))
        if not proposal:
            return {"msg": "Proposal not found!"}, 404
        student = Student.fetch(proposal.student_id)
        if student.is_approved:
            return {"msg": "Student already accepted by another advisor."}, 409
        elif advisor.advisor_id != proposal.advisor_id:
            return {"msg": "Unauthorised advisor."}, 403
        proposal.delete()
        advisor.set_advisor_to(student)  # Set the advisor's state.
        return {"msg": "Successful"}, 200

    @app.route('/students', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_managed_students() -> Tuple[Union[list, dict], int]:
        """
        Get a list of Students managed by this advisor.
        """
        advisor = current_user.downcast()
        if not isinstance(advisor, Advisor):  # If the current user is not an advisor.
            return {"msg": "Only the advisors can see their proposals."}, 403
        students = advisor.students
        return students, 200

    @app.route('/theses', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_student_theses() -> Tuple[Union[list, dict], int]:
        """
        Get a list of Theses uploaded so far by a student.
        """
        student = current_user.downcast()
        if not isinstance(student, Student):
            return {"msg": "Not authorised for this action."}, 403
        theses = student.theses
        return [thesis.thesis_id for thesis in theses], 200

    @app.route('/theses/<thesis_id>/metadata', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_thesis_metadata(thesis_id) -> Tuple[dict, int]:
        """
        Get metadata about a specific thesis.
        """
        thesis_id = int(thesis_id)
        if not Thesis.has(thesis_id):
            return {"msg": "Thesis not found."}, 404
        # TODO: If there is time we should check further for user's identity as well.
        thesis = Thesis.fetch(thesis_id)
        thesis_info = asdict(thesis)
        del thesis_info['file_path']  # It is better if the user is unaware of this.
        return thesis_info, 200

    @app.route('/theses/<thesis_id>', methods=['GET'])
    @jwt_required()
    def get_thesis_file(thesis_id) -> Response:
        """
        Get the actual file of the thesis that is requested.
        """
        thesis_id = int(thesis_id)
        if not Thesis.has(thesis_id):
            return Response(dumps({"msg": "Thesis not found."}), status=404, mimetype='application/json')
        # TODO: If there is time we should check further for user's identity as well.
        thesis = Thesis.fetch(thesis_id)
        thesis_info = asdict(thesis)
        thesis_path = thesis_info['file_path']  # It is better if the user is unaware of this.
        return send_file(os.path.join(os.getcwd(), thesis_path), mimetype='application/pdf')

    @app.route('/theses/<thesis_id>', methods=['DELETE'])
    @returns_json
    @jwt_required()
    def delete_thesis(thesis_id) -> Tuple[dict, int]:
        """
        Delete the thesis and associated metadata.
        """
        thesis_id = int(thesis_id)
        student = current_user.downcast()
        if not isinstance(student, Student):
            return {"msg": "Not authorised for this action."}, 403
        theses = student.theses  # TODO: If there is time we should check further for user's identity as well.
        if thesis_id not in [thesis.thesis_id for thesis in theses]:
            return {"msg": "Users cannot delete theses they do not own."}, 403
        thesis = Thesis.fetch(thesis_id)
        remove(os.path.join(os.getcwd(), thesis.file_path))  # Remove the thesis
        has_relationship = Has.fetch_where('thesis_id', thesis.thesis_id)[0]
        has_relationship.delete()  # Delete the ownership relationship
        thesis.delete()  # Delete the associated metadata.
        return {"msg": "Deleted thesis."}, 204

    @app.route('/theses', methods=['POST'])
    @returns_json
    @jwt_required()
    def upload_thesis() -> Tuple[dict, int]:
        """
        Post a thesis to the system and return its metadata.
        """
        student = current_user.downcast()
        if not isinstance(student, Student):
            return {"msg": "Not authorised for this action."}, 403
        elif 'file' not in request.files:
            return {"msg": "Files must contain a file with key file."}, 400
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(os.getcwd(), 'theses/', filename))  # Save to theses directory.
        file_path = os.path.join('theses/', filename)  # Relative file path.
        new_thesis_metadata = Thesis(-1, file_path, plagiarism_api.get_plagiarism_ratio(file_path),
                                     student.thesis_topic, round(time.time()))
        new_thesis_metadata.create()
        new_ownership = Has(-1, new_thesis_metadata.thesis_id, student.student_id)
        new_ownership.create()
        metadata = asdict(new_thesis_metadata)
        del metadata['file_path']
        return metadata, 201

    return app
