"""
This file includes the app routes.
"""
from flask import Flask


app = Flask(__name__) # Create the app object.


@app.route('/')
def hello_world():
    return """
    <html>
    <head>
    <title>MBS Backend</title>
    </head>
    <body>
    <iframe width="560" height="315" src="https://www.youtube.com/embed/_GY8nN105xE" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    </body>
    </html>
    """