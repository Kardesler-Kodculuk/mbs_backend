import sqlite3
from os import environ
import flask_unittest
import flask.globals
from flask import Response, request
from flask.testing import FlaskClient
from tests.expected_responses import expected_student_get_0, expected_advisor_get_1, expected_proposals, \
    expected_recommendations, expected_student

environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.
from mbsbackend import create_app


class TestUpdateStudentThesis(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "studenttest@std.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        with sqlite3.connect("test.db") as connection:
            cur = connection.cursor()
            cur.execute("UPDATE Student SET thesis_topic = 'Graph Visualisation' WHERE student_id = 0")
            connection.commit()  # Restore database to its original form.
        client.delete('/jwt')  # Logout.

    def test_set_student_thesis_topic(self, client: FlaskClient) -> None:
        resp = client.patch('students/0', json={"thesis_topic": "Parser Combinators"})
        self.assertStatus(resp, 200)
        expected_student_modified = expected_student_get_0
        expected_student_modified['thesis_topic'] = "Parser Combinators"
        self.assertDictEqual(resp.json, expected_student_modified)  # Let us check the return first.

    def test_set_student_thesis_topic_db(self, client: FlaskClient) -> None:
        """
        We are also going to check if the changes make it through to
            the database proper.
        """
        resp = client.patch("students/0", json={"thesis_topic": "Recursive Descent Parsers"})
        self.assertStatus(resp, 200)  # Just to make sure this one makes it through as well.
        with sqlite3.connect("test.db") as connection:
            cur = connection.cursor()
            cur.execute("SELECT thesis_topic FROM Student WHERE student_id = 0")
            topic = cur.fetchone()[0]
            self.assertEqual(topic, "Recursive Descent Parsers")


class TestUpdateStudentThesisInvalidJSON(flask_unittest.ClientTestCase):
    """
    Test if sending malformed JSON results in an error.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "studenttest@std.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        with sqlite3.connect("test.db") as connection:
            cur = connection.cursor()
            cur.execute("UPDATE Student SET thesis_topic = 'Graph Visualisation' WHERE student_id = 0")
            connection.commit()  # Restore database to its original form.
        client.delete('/jwt')  # Logout.

    def test_set_student_thesis_topic(self, client: FlaskClient) -> None:
        resp = client.patch('students/0', data="{thisisinvalidjson")  # Send malformed (literally not) JSON.
        self.assertStatus(resp, 400)
        # Let us check the return first.
        self.assertDictEqual(resp.json, {'msg': 'ERROR: Expected valid JSON in Request body.'})

