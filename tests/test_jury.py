import sqlite3
from os import environ
from sqlite3 import connect

import flask_unittest
import flask.globals
from flask import Response, request
from flask.testing import FlaskClient
from tests.expected_responses import expected_student_get_0, expected_advisor_get_1, expected_proposals, \
    expected_recommendations, expected_student_defending_list, expected_student_department_list, expected_jury_info, \
    expected_student_info_from_jury_advisor, expected_jury_members, jury_add_command

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
        Get students
        """
        resp = client.get('/students')
        self.assertStatus(resp, 200)
        self.assertDictEqual(expected_student_info_from_jury_advisor, resp.json)


class TestGetJuryFromAdvisor(flask_unittest.ClientTestCase):
    """
    Attempt to get jury members that can be proposed as a part of a dissertation.
    """

    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "hopkins@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_jury_members(self, client: FlaskClient) -> None:
        """
        Get the jury members as an advisor.
        """
        resp = client.get('/jury')
        self.assertStatus(resp, 200)
        self.assertDictEqual(expected_jury_members, resp.json)


class TestAddJuryAsAdvisor(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "hopkins@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.
        with connect('test.db') as db:
            cur = db.cursor()
            cur.execute(f"DELETE FROM Jury WHERE jury_id = {self.jury_id}")
            cur.execute(f"DELETE FROM User_ WHERE user_id = {self.jury_id}")
            db.commit()

    def test_add_jury_member(self, client: FlaskClient) -> None:
        """
        Attempt to add a jury member
        """
        resp = client.post('/jury', json=jury_add_command)
        self.assertStatus(resp, 201)
        self.jury_id = resp.json['user_id']
        self.assertLessEqual(jury_add_command.items(), resp.json.items())
