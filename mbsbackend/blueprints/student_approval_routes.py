from typing import Tuple, Union
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from dataclasses import asdict
from mbsbackend.datatypes.classes.user_classes import Student, Advisor, Jury, DBR
from mbsbackend.datatypes.classes.user_relationships import Proposal
from mbsbackend.datatypes.classes.user_utility import get_user
from mbsbackend.server_internals.consants import forbidden_fields
from mbsbackend.server_internals.verification import returns_json, full_json


def create_student_approval_routes() -> Blueprint:

    student_approval_routes = Blueprint('student_approval', __name__)

    @student_approval_routes.route('/students/<student_id>', methods=["GET"])
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

    @student_approval_routes.route('/students/<student_id>', methods=["PATCH"])
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
        if not Student.has(id_):
            return {"msg": "No such student."}, 404
        student = Student.fetch(id_)
        if isinstance(user, Student) and user.student_id == id_:
            payload = request.json
            acceptable_fields = [field for field in payload if
                                 field not in forbidden_fields["Student"] and field in Student.__dataclass_fields__]
            for field in acceptable_fields:
                setattr(user, field, payload[field])  # Update the field of the user.
            user.update()  # Update it in the database.
        elif isinstance(user, Advisor) and user.advisor_id == student.advisor.advisor_id:
            payload = request.json
            acceptable_fields = [field for field in payload if
                                 field not in forbidden_fields["StudentAdvisor"] and field in Student.__dataclass_fields__]
            for field in acceptable_fields:
                setattr(student, field, payload[field])  # Update the field of the user.
            student.update()  # Update it in the database.
        else:
            return {"msg": "Unauthorised"}, 401
        return get_user(Student, student.user_id), 200

    @student_approval_routes.route('/advisors/<advisor_id>', methods=["GET"])
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

    @student_approval_routes.route('/recommendations', methods=['GET'])
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

    @student_approval_routes.route('/proposals', methods=['GET'])
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

    @student_approval_routes.route('/proposals/<proposal_id>', methods=['DELETE'])
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

    @student_approval_routes.route('/proposals', methods=["POST"])
    @full_json(required_keys=('advisor_id',))
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

    @student_approval_routes.route('/proposals/<proposal_id>', methods=["PUT"])
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

    @student_approval_routes.route('/students', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_managed_students() -> Tuple[Union[list, dict], int]:
        """
        Get a list of Students managed by this advisor.
        """
        user = current_user.downcast()
        return_dict = {"students": [], "defenders": []}
        if not any(isinstance(user, accepted) for accepted in (Advisor, DBR, Jury)):  # If the current user is not an advisor.
            return {"msg": "Only the advisors can see their proposals."}, 403
        if any(isinstance(user, one_of) for one_of in (Advisor, DBR)):
            return_dict['students'] = user.students
        elif isinstance(user, Jury):
            return_dict['defenders'] = user.students  # All of these classes have a students property.
        if isinstance(user, Advisor) and user.jury_credentials:
            jury_version = user.jury_credentials
            return_dict['defenders'] = jury_version.students
        return return_dict, 200

    @student_approval_routes.route('/students/advisor/<student_id>', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_student_advisor(student_id) -> Tuple[dict, int]:
        """
        Get a specific student's advisor.
        """
        id_ = int(student_id)
        if not Student.has(id_):
            return {"msg": "Student not found."}, 404
        student = Student.fetch(id_)
        if not student.advisor:
            return {"msg": "Student does not have an advisor"}, 409
        return {"advisor": get_user(Advisor, student.advisor.advisor_id)}, 200


    return student_approval_routes
