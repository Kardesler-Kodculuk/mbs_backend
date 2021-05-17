import sqlite3
from os import environ
import flask_unittest
import flask.globals
from flask import Response, request
from flask.testing import FlaskClient
from tests.expected_responses import expected_student_get_0, expected_advisor_get_1, expected_proposals, \
    expected_recommendations, expected_student_defending_list, expected_student_department_list, expected_jury_info, \
    expected_student_info_from_jury_advisor

environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.
from mbsbackend import create_app


class TestGetJury(flask_unittest.ClientTestCase):
    """
    Get information about a jury member.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "obrien@metu.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_jury_information(self, client: FlaskClient) -> None:
        """
        Get information about a jury member.
        """
        resp = client.get('/jury/20')
        self.assertStatus(resp, 200)
        self.assertDictEqual(expected_jury_info, resp.json)


class TestGetAdvisorJury(flask_unittest.ClientTestCase):
    """
    Attempt to login and get students about an
        Advisor that is also a Jury.
    """

    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "hopkins@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_student_information(self, client: FlaskClient) -> None:
        """
        Get information about a jury member.
        """
        resp = client.get('/students')
        self.assertStatus(resp, 200)
        self.assertDictEqual(expected_student_info_from_jury_advisor, resp.json)

