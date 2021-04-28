from flask_jwt_extended import JWTManager

from mbsbackend import app
from os import getenv, urandom

app.config["SECRET_KEY"] = getenv("FLASK_SECRET_KEY", urandom(24))
app.config['JWT_AUTH_URL_RULE'] = '/jwt'
