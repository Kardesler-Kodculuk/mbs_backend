from os import environ
import flask_unittest
from flask.testing import FlaskClient
from tests.expected_responses import expected_dissertation

environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.
from mbsbackend import create_app


class TestGetDissertation(flask_unittest.ClientTestCase):
    """
    Get information about the dissertation of a student.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "obrien@metu.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_dissertation(self, client: FlaskClient) -> None:
        """
        Attempt to get information about a dissertation.
        """
        reply = client.get('/dissertation/22')  # Ask for dissertation for user 22.
        self.assertStatus(reply, 200)
        self.assertDictEqual(reply.json, expected_dissertation)

    def test_get_dissertation_fail(self, client: FlaskClient) -> None:
        """
        Attempt to get information about a dissertation that does not exist.
        """
        reply = client.get('/dissertation/10')  # Ask for dissertation for user 22.
        self.assertStatus(reply, 404)
