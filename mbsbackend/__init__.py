"""
This file includes the app routes.
"""
from datetime import datetime, timezone, timedelta
from typing import Tuple
from flask_cors import CORS
from flask import Flask, g, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, current_user, create_access_token, set_access_cookies, \
    unset_jwt_cookies, get_jwt_identity, get_jwt
from dataclasses import asdict
from mbsbackend.datatypes.classes import User_, Student, Advisor
from mbsbackend.server_internals.authentication import authenticate, identity
from mbsbackend.server_internals.verificiaton import json_required
from mbsbackend.server_internals.global_config import GlobalConfig


app = Flask(__name__)  # Create the app object.
jwt = JWTManager(app)
global_config = GlobalConfig()
global_config.testing = True
CORS(app, resources={r"/jwt/*": {"origins": "http://localhost:3000"},
                     r"/user/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)


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
    cur_user: User_ = User_.fetch(current_user.user_id)
    subuser = cur_user.downcast()  # Downcast the user.
    user_info = {}
    if isinstance(subuser, Student) and subuser.advisor:
        user_info['role'] = 'student'  # Set the role.
        user_info['student'] = asdict(cur_user)
        user_info['student']['username'] = user_info['student']['name_']
        user_info['advisor'] = asdict(cur_user.advisor)
    elif isinstance(subuser, Student) and not subuser.advisor:
        user_info['role'] = 'student'
        user_info['student'] = asdict(cur_user)
        user_info['username'] = cur_user.name_
    elif isinstance(subuser, Advisor):
        user_info['role'] = 'advisor'
        user_info['advisor'] = asdict(cur_user)
    else:
        return "Invalid user type", 400
    return jsonify(user_info), 200
