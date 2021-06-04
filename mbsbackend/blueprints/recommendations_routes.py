"""
This file includes the app routes used for recommending users.
"""
from typing import Tuple
from flask import request, Blueprint
from flask_jwt_extended import jwt_required, current_user
from mbsbackend.datatypes.classes.user_classes import Student, DBR
from mbsbackend.datatypes.classes.user_classes import Recommended
from mbsbackend.server_internals.verification import returns_json, full_json


def create_recommendations_routes() -> Blueprint:

    recommendations_routes = Blueprint('recommendations_routes', __name__)

    @recommendations_routes.route('/recommendations/<student_id>', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_recommendations_of(student_id: str) -> Tuple[dict, int]:
        """
        Get the recommendations of the student, as DBR.
        """
        dbr = current_user.downcast()
        if not isinstance(dbr, DBR):
            return {"msg": "Unauthorised"}, 403
        id_ = int(student_id)
        if not Student.has(id_):
            return {"msg": "Student not found."}, 404
        student: Student = Student.fetch(id_)
        if student.department_id != dbr.department_id:
            return {"msg": "Unauthorised to view this student"}, 403
        recommendations = student.recommendations
        return {"recommended_advisors": [recommendation.advisor_id for recommendation in recommendations]}, 200

    @recommendations_routes.route('/recommendations/needed', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_students_needing_recommendations() -> Tuple[dict, int]:
        """
        Get a list of students that need recommendations.
        """
        dbr = current_user.downcast()
        if not isinstance(dbr, DBR):
            return {"msg": "Unauthorized"}, 403
        return {"students_without_recommendations": dbr.students_without_recommendations}, 200

    @recommendations_routes.route('/recommendations/<student_id>', methods=['POST'])
    @full_json(required_keys=('advisor_id',))
    @jwt_required()
    def post_recommendations(student_id: str) -> Tuple[dict, int]:
        """
        Post a new recommendation for a student, as DBR.
        """
        dbr = current_user.downcast()
        if not isinstance(dbr, DBR):
            return {"msg": "Unauthorised"}, 403
        id_ = int(student_id)
        if not Student.has(id_):
            return {"msg": "Student not found."}, 404
        student: Student = Student.fetch(id_)
        if student.department_id != dbr.department_id:
            return {"msg": "Unauthorised to view this student"}, 403
        new_recommendation = Recommended(-1, int(student_id), request.json['advisor_id'])
        new_recommendation.create()
        return {"msg": "Recommendation created."}, 201

    @recommendations_routes.route('/advisors', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_department_advisors() -> Tuple[dict, int]:
        """
        Get all advisors in a department, as DBR.
        """
        dbr = current_user.downcast()
        if not isinstance(dbr, DBR):
            return {"msg": "Unauthorised"}, 403
        advisors = dbr.advisors
        return {"advisors": advisors}, 200

    return recommendations_routes
