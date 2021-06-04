import sqlite3
from os import environ
import flask_unittest
from flask.testing import FlaskClient
from tests.expected_responses import expected_student_get_0
environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.
from mbsbackend import create_app


class TestUpdateStudentThesis(flask_unittest.ClientTestCase):
    app = create_app()

    def test_reset_database(self, client: FlaskClient) -> None:
        """
        Test if we can reset the database.
        """
        resp = client.get("/system/reset")
        self.assertStatus(resp, 204)  # Just to make sure this one makes it through as well.
        resp = client.get("/")
        self.assertStatus(resp, 200)
