"""
This file includes the app routes.
"""
from typing import Tuple
from flask import request, Blueprint
from flask_jwt_extended import jwt_required, current_user
from mbsbackend.datatypes.classes.user_classes import Student, Advisor, DBR, Jury
from mbsbackend.datatypes.classes.user_utility import get_user
from mbsbackend.datatypes.classes.thesis_classes import Evaluation
from mbsbackend.server_internals.verification import returns_json, full_json


def create_dissertation_routes():
    dissertation_routes = Blueprint('dissertation_routes', __name__)

    @dissertation_routes.route('/jury', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_jury_all() -> Tuple[dict, int]:
        """
        An advisor can get all the jury members in
            their own department using this.
        """
        advisor = current_user.downcast()
        if not isinstance(advisor, Advisor):
            return {"msg": "Only advisor can view the jury member list."}, 403
        jury_members = Jury.fetch_where('department_id', advisor.department_id)
        return {"jury_members": [jury.jury_id for jury in jury_members]}, 200

    @dissertation_routes.route('/jury', methods=['POST'])
    @full_json(requiried_keys=('name_', 'surname', 'email', 'institution', 'phone_number'))
    @jwt_required()
    def post_jury() -> Tuple[dict, int]:
        """
        An advisor can add a new, external Jury member to the system.
        """
        advisor = current_user.downcast()
        req: dict = request.json
        if not isinstance(advisor, Advisor):
            return {"msg": "Only advisor add a new jury member."}, 403
        new_jury_member = Jury.add_new_jury(
            [-1,
            req['name_'],
            req['surname'],
            "dflkjgdfjkgkdfgfd",
            req['email'],
            advisor.department_id],
            [-1,
            False,
            req['institution'],
            req['phone_number'],
            True]
        )
        return get_user(Jury, new_jury_member.jury_id), 201

    @dissertation_routes.route('/jury/<jury_id>', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_jury(jury_id) -> Tuple[dict, int]:
        """
        Get a jury information given its id.

        :param jury_id: ID of the Jury to get the information.
        :return The jury member's credentials.
        """
        id_ = int(jury_id)
        if not Jury.has(id_):
            return {"msg": "Jury member not found."}, 404
        return get_user(Jury, id_), 200

    @dissertation_routes.route('/dissertation/<student_id>', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_dissertation_info(student_id) -> Tuple[dict, int]:
        """
        Get a dissertation information with addition of Jury members.

        :param student_id: Student ID of the Student whose dissertation
         we are reaching.
        """
        id_ = int(student_id)
        if not Student.has(id_):
            return {"msg": "Student now found."}, 404
        dissertation_info = Student.fetch(id_).dissertation_info
        if dissertation_info:
            return dissertation_info, 200
        else:
            return {"msg": "Student does not have a dissertation."}, 404

    @dissertation_routes.route('/dissertation/<student_id>', methods=['POST'])
    @full_json(required_keys=('jury_members', 'dissertation_date'))
    @jwt_required()
    def create_new_dissertation(student_id) -> Tuple[dict, int]:
        """
        Create a new dissertation.

        :param student_id: Student ID of the Student whose dissertation
         we creating.
        """
        id_ = int(student_id)
        advisor = current_user.downcast()
        if not isinstance(advisor, Advisor):
            return {'msg': 'Requries advisor user to do this.'}, 403
        elif not Student.has(id_):
            return {'msg': 'Student not found.'}, 404
        student = Student.fetch(id_)
        if student.advisor.advisor_id != advisor.advisor_id:
            return {"msg": "Not the advisor of this student."}, 403
        elif student.dissertation_info:
            return {"msg": "Student already has one [possibly proposed] dissertation."}, 409
        dissertation = student.create_dissertation_for(request.json['jury_members'], request.json['dissertation_date'])
        if dissertation is None:
            return {"msg": "Jury member not found"}, 404
        return {"msg": "Dissertation is created."}, 201

    @dissertation_routes.route('/dissertation/<student_id>', methods=['DELETE'])
    @jwt_required()
    def reject_dissertation(student_id) -> Tuple[dict, int]:
        """
        Reject a dissertation proposal.
        """
        user = current_user.downcast()
        id_ = int(student_id)
        if not Student.has(id_):
            return {"msg": "Student not found."}, 404
        student: Student = Student.fetch(id_)
        if not isinstance(user, DBR) or student.department_id != user.department_id:
            return {"msg": "You are unauthorised for this action."}, 403
        if student.dissertation_info:
            dissertation = student.dissertation
            if dissertation.is_approved:
                return {"msg": "Cannot reject an approved dissertation."}, 409
            dissertation.delete_dissertation()  # Delete the object.
        return {"msg": "Dissertation object no longer exists."}, 204

    @dissertation_routes.route('/dissertation/<student_id>', methods=['PUT'])
    @jwt_required()
    def accept_dissertation_proposal(student_id) -> Tuple[dict, int]:
        """
        Accept a dissertation proposal.
        """
        user = current_user.downcast()
        id_ = int(student_id)
        if not Student.has(id_):
            return {"msg": "Student not found."}, 404
        student: Student = Student.fetch(id_)
        if not isinstance(user, DBR) or student.department_id != user.department_id:
            return {"msg": "You are unauthorised for this action."}, 403
        if student.dissertation_info:
            dissertation = student.dissertation
            dissertation.is_approved = True
            dissertation.update()  # Delete the object.
            return student.dissertation_info, 200
        else:
            return {"msg": "Student does not have dissertation"}, 409

    @dissertation_routes.route('/evaluation/<student_id>', methods=['POST'])
    @full_json(required_keys=('evaluation',))
    @jwt_required()
    def post_evaluation(student_id) -> Tuple[dict, int]:
        """
        Evaluate a thesis as a jury member.
        """
        if request.json['evaluation'] not in ('Correction', 'Rejected', 'Approved'):
            return {"msg": "Invalid evaluation."}, 409
        user = current_user.downcast()
        id_ = int(student_id)
        if not Student.has(id_):
            return {"msg": "Student not found."}, 404
        student: Student = Student.fetch(id_)
        if (not isinstance(user, Advisor) and not isinstance(user, Jury)) or not user.can_evaluate(student):
            return {"msg": "Unauthorized"}, 403
        dissertation = student.dissertation
        evaluation = Evaluation(-1, dissertation.dissertation_id, user.user_id, request.json['evaluation'])
        evaluation.create()
        return {"msg": "Created."}, 201

    @dissertation_routes.route('/evaluation/<student_id>', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_evaluation(student_id) -> Tuple[dict, int]:
        """
        Get your evaluation.
        """
        user = current_user.downcast()
        id_ = int(student_id)
        if not Student.has(id_):
            return {"msg": "Student not found."}, 404
        student: Student = Student.fetch(id_)
        if (not isinstance(user, Advisor) and not isinstance(user, Jury)) or not user.can_evaluate(student):
            return {"msg": "Unauthorized"}, 403
        dissertation = student.dissertation
        evaluation = Evaluation.fetch_where('dissertation_id', dissertation.dissertation_id)
        evaluation = (*filter(lambda e: e.jury_id == user.user_id, evaluation),)
        if evaluation:
            return {"evaluation": evaluation[0].evaluation}, 200
        return {"msg": "Not found."}, 404

    return dissertation_routes
