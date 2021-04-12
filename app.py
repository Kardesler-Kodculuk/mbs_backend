from src.backend import app
from os import getenv, urandom

app.config["SECRET_KEY"] = getenv("FLASK_SECRET_KEY", urandom(24))
