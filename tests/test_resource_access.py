# Resource access tests, including GET Requests to single resources,
#   and PATCH requests.
from os import environ
import flask_unittest
import flask.globals
from flask import Response, request
from flask.testing import FlaskClient
from tests.expected_responses import expected_student_get_0, expected_advisor_get_1

environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.
from mbsbackend import create_app


class TestGetResources(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "advisortest@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_student(self, client: FlaskClient) -> None:
        resp = client.get('students/0')
        self.assertStatus(resp, 200)
        self.assertDictEqual(resp.json, expected_student_get_0)

    def test_get_student_fail(self, client: FlaskClient) -> None:
        resp = client.get('students/1')
        self.assertStatus(resp, 400)

    def test_get_advisor(self, client: FlaskClient) -> None:
        resp = client.get('advisors/1')
        self.assertStatus(resp, 200)
        self.assertDictEqual(resp.json, expected_advisor_get_1)

    def test_get_advisor_fail(self, client: FlaskClient) -> None:
        resp = client.get('advisors/2')
        self.assertStatus(resp, 400)

