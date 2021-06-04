"""
This file includes the app routes.
"""
from datetime import datetime, timezone, timedelta
from os import getenv, urandom, remove
from flask_cors import CORS
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, get_jwt_identity, get_jwt

from mbsbackend.blueprints.form_routes import create_form_routes
from mbsbackend.datatypes.classes.user_classes import User_
from mbsbackend.datatypes.classes.user_utility import convert_department, get_user
from mbsbackend.datatypes.database import global_query_handler
from mbsbackend.external_services.plagiarism_api import PlagiarismManager
from mbsbackend.server_internals.authentication import authenticate
from mbsbackend.server_internals.consants import version_number
from mbsbackend.blueprints import *


def create_app() -> Flask:
    """
    This is a typical use of the create app function in flask.
        although I recognise this looks complex, it is not a
        typical function.
    """
    app = Flask(__name__)  # Create the app object.
    jwt = JWTManager(app)
    plagiarism_api = PlagiarismManager()
    CORS(app, supports_credentials=True)

    app.config["SECRET_KEY"] = getenv("FLASK_SECRET_KEY", urandom(24))
    app.config['JWT_AUTH_URL_RULE'] = '/jwt'
    app.config['DEBUG'] = False
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    app.register_blueprint(create_student_approval_routes())
    app.register_blueprint(create_thesis_management_routes(plagiarism_api))
    app.register_blueprint(create_dissertation_routes())
    app.register_blueprint(create_login_routes())
    app.register_blueprint(create_recommendations_routes())
    app.register_blueprint(create_form_routes())

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

    return app
