from os import environ
from sqlite3 import connect

import flask_unittest
from flask.testing import FlaskClient

from tests.expected_responses import expected_dissertation, dissertation_add_json, dissertation_expected_json

environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.
from mbsbackend import create_app


class TestGetEvaluation(flask_unittest.ClientTestCase):
    """
    Try to get evaluation.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "hopkins@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_evaluation(self, client: FlaskClient) -> None:
        """
        Attempt to get the evaluation done on a student's dissertation prior.
        """
        reply = client.get('/evaluation/22')  # Ask for dissertation for user 22.
        self.assertStatus(reply, 200)
        self.assertEqual(reply.json['evaluation'], "Approved")


class TestPostEvaluation(flask_unittest.ClientTestCase):
    """
    Try to Post an evaluation
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "obrien@metu.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.
        with connect('test.db') as db:
            cur = db.cursor()
            cur.execute('DELETE FROM Evaluation WHERE jury_id = 20')
            db.commit()

    def test_post_evaluation(self, client: FlaskClient) -> None:
        """
        Attempt to post an evaluation.
        """
        reply = client.post('/evaluation/22', json={'evaluation': 'Rejected'})
        self.assertStatus(reply, 201)
        reply = client.get('/evaluation/22')
        self.assertStatus(reply, 200)
        self.assertEqual(reply.json['evaluation'], 'Rejected')
