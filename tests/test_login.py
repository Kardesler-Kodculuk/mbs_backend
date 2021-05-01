from os import environ

import flask_unittest
import flask.globals
from flask import Response, request
from flask.testing import FlaskClient
from tests.expected_responses import expected_student

environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.


class TestLogin(flask_unittest.ClientTestCase):
    from mbsbackend import create_app
    """
    Test the POST request to /jwt which is to
        login a user.
    """

    app = create_app()  # Create our app.

    def test_login_fail(self, client: FlaskClient) -> None:
        resp = client.post('/jwt', json={"username": "maryshelley", "password": "modernprometheus"})
        self.assertStatus(resp, 401)  # Check if the user log in failed.

    def test_login_success(self, client: FlaskClient) -> None:
        resp: Response = client.post('/jwt', json={"username": "studenttest@std.iyte.edu.tr", "password": "test+7348"})
        self.assertStatus(resp, 201)   # Should create new session.
        self.assertIn("access_token", resp.json)
        self.assertIn("access_token_cookie", client.cookie_jar._cookies['localhost.local']['/'])


class TestLogout(flask_unittest.ClientTestCase):
    from mbsbackend import create_app
    """
    Test the logout functionality achieved via DELETE
        to /jwt.
    """

    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "studenttest@std.iyte.edu.tr", "password": "test+7348"})

    def test_logout_success(self, client: FlaskClient) -> None:
        resp = client.delete('/jwt')
        self.assertStatus(resp, 204)
        self.assertNotIn("access_token", flask.globals.session)


class TestLoginStudentNoAdvisor(flask_unittest.ClientTestCase):
    from mbsbackend import create_app
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "studenttest@std.iyte.edu.tr", "password": "test+7348"})

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_student_login(self, client: FlaskClient) -> None:
        resp = client.get('/users')
        self.assertStatus(resp, 200)
        self.assertDictEqual(expected_student, resp.json)

