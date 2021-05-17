# Resource access tests, including GET Requests to single resources,
#   and PATCH requests.
import sqlite3
from os import environ
import flask_unittest
import flask.globals
from flask import Response, request
from flask.testing import FlaskClient
from tests.expected_responses import expected_student_get_0, expected_advisor_get_1, expected_proposals, \
    expected_recommendations, expected_student_defending_list, expected_student_department_list

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


class TestRecommendations(flask_unittest.ClientTestCase):
    """
    Test if we can see recommendations
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "studenttest2@std.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_recommendations(self, client: FlaskClient) -> None:
        resp = client.get('/recommendations')
        self.assertCountEqual(resp.json, expected_recommendations)


class TestGetManagedStudentIDs(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "doyle@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_recommendations(self, client: FlaskClient) -> None:
        resp = client.get('/students')
        self.assertCountEqual(resp.json, [7, 8])


class TestGetDefending(flask_unittest.ClientTestCase):
    """
    Test if a jury can log in and get a list of students defending their dissertations.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "obrien@metu.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_dissertation_defenders(self, client: FlaskClient) -> None:
        resp = client.get('/students')
        self.assertStatus(resp, 200)
        self.assertCountEqual(resp.json, expected_student_defending_list)


class TestGetDepartmentStudents(flask_unittest.ClientTestCase):
    """
    Test if a DBR can log in and get a list of students in their department.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "lord@pers.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_dissertation_defenders(self, client: FlaskClient) -> None:
        resp = client.get('/students')
        self.assertStatus(resp, 200)
        self.assertCountEqual(resp.json, expected_student_department_list)
