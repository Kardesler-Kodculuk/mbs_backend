from os import environ

import flask_unittest
from flask.testing import FlaskClient

environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.
from mbsbackend import create_app


class TestRestrictedEndpoint(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "doyle@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_advisors(self, client: FlaskClient) -> None:
        """
        Attempt to get the advisors endpoint. Should fail since
            only DBR can.
        """
        resp = client.get('/advisors')
        self.assertStatus(resp, 403)
