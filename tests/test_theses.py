import sqlite3
from os import environ
import flask_unittest
from hashlib import md5
from flask.testing import FlaskClient
from tests.expected_responses import expected_pdf_file_name, expected_theses_list, expected_thesis_metadata_get

environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.
from mbsbackend import create_app


class TestGetTheses(flask_unittest.ClientTestCase):
    """
    Test if a student can access their theses successfully.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "grey@std.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_thesis_list(self, client: FlaskClient) -> None:
        """
        Check if the student can get a list of their theses.
        """
        resp = client.get('/theses')  # We are expecting a list of thesis ids.
        self.assertStatus(resp, 200)
        self.assertCountEqual(resp.json, expected_theses_list)  # Let us check the return first.

    def test_get_thesis_metadata(self, client: FlaskClient) -> None:
        """
        Check if the student can get the metadata of a specific thesis.
        """
        resp = client.get('/theses/0/metadata')
        self.assertStatus(resp, 200)
        self.assertDictEqual(resp.json, expected_thesis_metadata_get)

    def test_get_thesis_metadata_fail(self, client: FlaskClient) -> None:
        """
        Attempt to get a nonexistent thesis' metadata.
        """
        resp = client.get('/theses/10000/metadata')
        self.assertStatus(resp, 404)

    def test_get_thesis_file(self, client: FlaskClient) -> None:
        resp = client.get('/theses/0')
        self.assertStatus(resp, 200)
        with open(expected_pdf_file_name, 'rb') as fp:
            data = fp.read()
            expected_hash = md5(data)
        actual_hash = md5(resp.data)
        resp.close()
        self.assertEqual(actual_hash.digest(), expected_hash.digest())

    def test_get_thesis_file_fail(self, client: FlaskClient) -> None:
        resp = client.get('/theses/10000')
        self.assertStatus(resp, 404)
