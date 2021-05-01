from flask_jwt_extended import JWTManager

from mbsbackend import create_app
from os import getenv, urandom

app = create_app()

