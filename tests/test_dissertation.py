
from os import environ
from sqlite3 import connect

import flask_unittest
from flask.testing import FlaskClient

from tests.expected_responses import expected_dissertation, dissertation_add_json, dissertation_expected_json

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


class TestRejectDissertation(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "lord@pers.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.
        with connect('test.db') as db:
            cur = db.cursor()
            cur.executescript("""INSERT INTO Dissertation VALUES (3, 1621129276, FALSE);
INSERT INTO Member VALUES (4, 3, 23);
INSERT INTO Defending VALUES (3, 3, 21);
INSERT INTO Member VALUES (5, 3, 20);""")

    def test_reject_dissertation(self, client: FlaskClient) -> None:
        """
        Reject a proposed dissertation.
        """
        resp = client.delete('/dissertation/21')
        self.assertStatus(resp, 204)
        with connect('test.db') as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM Dissertation WHERE dissertation_id = 3")
            self.assertIsNone(cur.fetchone(), "Dissertation object is not deleted.")
            cur.execute("SELECT * FROM Member WHERE dissertation_id = 3")
            self.assertIsNone(cur.fetchone(), "Member objects are not deleted.")
            cur.execute("SELECT * FROM Defending WHERE dissertation_id = 3")
            self.assertIsNone(cur.fetchone(), "Defending object is not deleted.")


class TestRejectDissertationFailure(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "lord@pers.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_reject_dissertation_fail(self, client: FlaskClient) -> None:
        """
        Attempt to reject a already approved dissertation.
        """
        resp = client.delete('dissertation/22')
        self.assertStatus(resp, 409)


class TestProposeDissertation(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "oliver@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.
        with connect('test.db') as db:
            cur = db.cursor()
            cur.execute("SELECT dissertation_id FROM Defending WHERE student_id = 26")
            dissertation_id = cur.fetchone()[0]
            cur.execute("DELETE FROM Dissertation WHERE dissertation_id = (?)", (dissertation_id,))
            cur.execute("DELETE FROM Defending WHERE dissertation_id = (?)", (dissertation_id,))
            cur.execute("DELETE FROM Member WHERE dissertation_id = (?)", (dissertation_id,))
            db.commit()

    def test_propose_dissertation(self, client: FlaskClient) -> None:
        """
        Attempt to propose a new dissertation with a date and jury members
        """
        resp = client.post('dissertation/26', json=dissertation_add_json)
        self.assertStatus(resp, 201)
        resp = client.get('dissertation/26')
        self.assertDictEqual(dissertation_expected_json, resp.json)


class TestProposeDissertationFail(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "oliver@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_propose_dissertation_fail(self, client: FlaskClient) -> None:
        """
        Attempt to propose a new dissertation with a date and jury members
            when the user already has one.
        """
        resp = client.post('dissertation/17', json=dissertation_add_json)
        self.assertStatus(resp, 409)


class TestApproveDissertation(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "lord@pers.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.
        with connect("test.db") as db:
            cur = db.cursor()
            cur.execute("UPDATE Dissertation SET is_approved = FALSE WHERE dissertation_id = 3")
            db.commit()

    def test_approve_dissertation(self, client: FlaskClient) -> None:
        """
        Attempt to propose a new dissertation with a date and jury members
            when the user already has one.
        """
        resp = client.put('/dissertation/21')
        self.assertStatus(resp, 200)
        resp = client.get('/dissertation/21')
        self.assertEqual(resp.json['status'], 'Undecided')

