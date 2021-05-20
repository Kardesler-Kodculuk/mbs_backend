from typing import Tuple
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, current_user, create_access_token, set_access_cookies, \
    unset_jwt_cookies
from dataclasses import asdict
from mbsbackend.datatypes.classes.user_classes import User_, Student, Advisor, DBR, Jury
from mbsbackend.datatypes.classes.user_utility import convert_department
from mbsbackend.server_internals.authentication import authenticate
from mbsbackend.server_internals.verification import returns_json


def create_login_routes() -> Blueprint:

    login_routes = Blueprint('login_routes', __name__)

    @login_routes.route('/jwt', methods=['POST'])
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

    @login_routes.route('/jwt', methods=['DELETE'])
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

    @login_routes.route('/users', methods=["GET"])
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
            if user.jury_credentials:
                user_info['jury'] = asdict(user.jury_credentials)
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

    return login_routes
