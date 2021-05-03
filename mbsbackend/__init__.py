"""
This file includes the app routes.
"""
from datetime import datetime, timezone, timedelta
from os import getenv, urandom
from typing import Tuple
from flask_cors import CORS
from flask import Flask, g, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, current_user, create_access_token, set_access_cookies, \
    unset_jwt_cookies, get_jwt_identity, get_jwt
from dataclasses import asdict
from mbsbackend.datatypes.classes import User_, Student, Advisor, Proposal, get_user, Recommended, Instructor
from mbsbackend.server_internals.authentication import authenticate, identity
from mbsbackend.server_internals.consants import forbidden_fields
from mbsbackend.server_internals.verification import json_required


def create_app() -> Flask:
    """
    This is a typical use of the create app function in flask.
        although I recognise this looks complex, it is not a
        typical function.
    """
    app = Flask(__name__)  # Create the app object.
    jwt = JWTManager(app)
    CORS(app,  supports_credentials=True)
    app.config["SECRET_KEY"] = getenv("FLASK_SECRET_KEY", urandom(24))
    app.config['JWT_AUTH_URL_RULE'] = '/jwt'
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    @app.route('/')
    def test_url():
        return "Server running correctly on heroku.", 200

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
    @jwt_required()
    def get_user_information() -> Tuple[str, int]:
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
            del user_info['student']['password']  # We should not let client see the hash.
            user_info['advisor'] = asdict(user.advisor)
            del user_info['advisor']['password']  # Likewise, the client should definetly not see this hash.
        elif isinstance(user, Student) and not user.advisor:
            user_info['role'] = 'student'
            user_info['student'] = asdict(user)
            user_info['username'] = user_info['student']['name_']  # Remove in Production. Backward Compatibility.
            del user_info['student']['password']  # We should not let client see the hash.
            user_info['username'] = user.name_
        elif isinstance(user, Advisor):
            user_info['role'] = 'advisor'
            user_info['advisor'] = asdict(user)
            user_info['username'] = user_info['advisor']['name_']  # Remove in Production. Backward Compatibility.
            del user_info['advisor']['password']  # We should not let client see the hash.
        else:
            return "Invalid user type", 400
        return jsonify(user_info), 200

    @app.route('/students/<student_id>', methods=["GET"])
    @jwt_required()
    def get_student_information(student_id: str) -> Tuple[str, int]:
        """
        Get user information of a specific student.
        """
        student = get_user(Student, int(student_id))
        if student is None:
            return jsonify({'msg': 'Student not found.'}), 400
        return jsonify(student), 200

    @app.route('/students/<student_id>', methods=["PATCH"])
    @jwt_required()
    def update_student_information(student_id: str) -> Tuple[str, int]:
        """
        Update information on a student, given that the student is the
            current user.

        TODO: In the future, this endpoint will support advisor doing changes.
        """
        user = current_user.downcast()
        id_ = int(student_id)
        if not isinstance(user, Student) and user.student_id != student_id:
            return jsonify({"msg": "Unauthorised"}), 401
        payload = request.json
        acceptable_fields = [field for field in payload if
                             field not in forbidden_fields["Student"] and field in Student.__dataclass_fields__]
        for field in acceptable_fields:
            setattr(user, field, payload[field])  # Update the field of the user.
        user.update()  # Update it in the database.
        return jsonify(get_user(Student, user.user_id)), 200

    @app.route('/advisors/<advisor_id>', methods=["GET"])
    @jwt_required()
    def get_advisor_information(advisor_id: str) -> Tuple[str, int]:
        """
        Get user information about a specific advisor.
        """
        advisor = get_user(Advisor, int(advisor_id))
        if advisor is None:
            return jsonify({"msg": 'Advisor not found.'}), 400
        return jsonify(advisor), 200

    @app.route('/recommendations', methods=['GET'])
    @jwt_required()
    def get_recommendations() -> Tuple[str, int]:
        """
        Get the recommendations (advisor recommendations) for
            the currently logged in Student user.
        """
        student = current_user.downcast()
        if not isinstance(student, Student):
            return jsonify({"msg": "Only the student may have recommendations"}), 403
        elif student.has_proposed:
            return jsonify({"msg": "Already proposed to an advisor"}), 409
        recommendations = student.recommendations
        if not recommendations:
            return jsonify({"msg": "No recommended advisors found."}), 404
        # If there are recommendations, convert them to dictionaries and return them as JSON.
        return jsonify([asdict(recommendation) for recommendation in recommendations]), 200

    @app.route('/proposals', methods=['GET'])
    @jwt_required()
    def get_proposals() -> Tuple[str, int]:
        """
        Get a list of proposals made to this Advisor user
            that is currently logged in.
        """
        advisor = current_user.downcast()
        if not isinstance(advisor, Advisor):  # If the current user is not an advisor.
            return jsonify({"msg": "Only the advisors can see their proposals."}), 403
        proposals = advisor.proposals
        return jsonify([asdict(proposal) for proposal in proposals]), 200

    @app.route('/proposals/<proposal_id>', methods=['DELETE'])
    @jwt_required()
    def reject_proposal(proposal_id: str) -> Tuple[str, int]:
        """
        Reject a proposal by deleting it from the
            database. This also turns the student's
            has_proposed into false.
        """
        advisor = current_user.downcast()
        if not isinstance(advisor, Advisor):  # If the current user is not an advisor.
            return jsonify({"msg": "Only the advisors can see their proposals."}), 403
        proposal = Proposal.has(proposal_id) and Proposal.fetch(proposal_id)
        if not proposal:
            return jsonify({"msg": "Proposal deleted."}), 204  # Since DELETE is idempotent, this is alright.
        if not proposal.advisor_id == advisor.advisor_id:
            return jsonify({"msg": "You aren't authorised for this."}), 401
        proposal.delete()
        student = Student.fetch(proposal.student_id)
        student.has_proposed = False
        student.update()
        return "", 204

    @app.route('/proposals', methods=["POST"])
    @jwt_required()
    def create_new_proposal() -> Tuple[str, int]:
        """
        A student user may create a proposal to an advisor
            user, provided that they're in their recommended list of
            advisors.
        """
        payload = request.json
        student = current_user.downcast()
        if not isinstance(student, Student):
            return jsonify({"msg": "Unauthorised."}), 403
        advisor_id = payload["advisor_id"]
        student_recommended_advisors = [recommendation.advisor_id for recommendation in student.recommendations]
        if student.has_proposed:
            return jsonify({"msg": "Already proposed."}), 409
        elif advisor_id not in student_recommended_advisors:  # If this student was not recommended their advisor.
            return jsonify({"msg": "Advisor is not recommended to the user."}), 409
        elif not Advisor.has(advisor_id):
            return jsonify({"msg": "No such advisor."}), 404
        else:  # Otherwise we are fine and can propose.
            student.has_proposed = True
            student.update()
            proposal_ = Proposal(-1, student.student_id, advisor_id)
            proposal_.create()
            return jsonify(asdict(proposal_)), 201

    @app.route('/proposals/<proposal_id>', methods=["PUT"])
    @jwt_required()
    def approve_proposal(proposal_id: str) -> Tuple[str, int]:
        """
        An advisor user can approve the proposals made to them.
        """
        advisor = current_user.downcast()
        if not isinstance(advisor, Advisor):
            return jsonify({"msg": "Unauthorised."}), 403
        proposal = Proposal.has(int(proposal_id)) and Proposal.fetch(int(proposal_id))
        if not proposal:
            return jsonify({"msg": "Proposal not found!"}), 404
        student = Student.fetch(proposal.student_id)
        if student.is_approved:
            return jsonify({"msg": "Student already accepted by another advisor."}), 409
        elif advisor.advisor_id != proposal.advisor_id:
            return jsonify({"msg": "Unathorised advisor."}), 403
        proposal.delete()
        advisor.set_advisor_to(student)  # Set the advisor's state.
        return jsonify({"msg": "Successful"}), 200

    @app.route('/students', methods=['GET'])
    @jwt_required()
    def get_managed_students() -> Tuple[str, int]:
        """
        Get a list of Students managed by this advisor.
        """
        advisor = current_user.downcast()
        if not isinstance(advisor, Advisor):  # If the current user is not an advisor.
            return jsonify({"msg": "Only the advisors can see their proposals."}), 403
        students = advisor.students
        return jsonify(students), 200


    return app
