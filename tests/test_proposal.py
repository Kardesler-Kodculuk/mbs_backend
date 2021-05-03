# Tests for the Proposals collection and the Proposal resources.
import sqlite3
from os import environ
import flask_unittest
import flask.globals
from flask import Response, request
from flask.testing import FlaskClient
from tests.expected_responses import expected_student_get_0, expected_advisor_get_1, expected_proposals, \
    expected_recommendations
environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.
from mbsbackend import create_app, Student, Advisor


class TestProposalsForAdvisor(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "bouwman@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_proposals(self, client: FlaskClient) -> None:
        resp = client.get('proposals')
        self.assertStatus(resp, 200)
        self.assertCountEqual(resp.json, expected_proposals)


class TestProposalReject(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "bouwman@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.
        with sqlite3.connect("test.db") as test_con:
            cur = test_con.cursor()
            cur.execute("INSERT INTO Proposal VALUES (0, 4, 3)")  # Put everything back to its place.
            cur.execute("UPDATE Student SET has_proposed = TRUE WHERE student_id = 4")
            test_con.commit()

    def test_reject_proposal(self, client: FlaskClient) -> None:
        resp = client.delete('proposals/0')
        self.assertStatus(resp, 204)
        with sqlite3.connect("test.db") as test_con:
            cur = test_con.cursor()
            cur.execute("SELECT * FROM Proposal WHERE proposal_id = 0")
            results = cur.fetchone()
            self.assertIsNone(results)
        resp2 = client.get('students/4')
        self.assertEqual(resp2.json['has_proposed'], 0)  # Check if proposed is set to 0 sucessfully.


class TestProposalAccept(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "bouwman@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.
        with sqlite3.connect("test.db") as test_con:
            cur = test_con.cursor()
            cur.execute("INSERT INTO Proposal VALUES (1, 5, 3)")  # Put everything back to its place.
            cur.execute("UPDATE Student SET is_approved = FALSE WHERE student_id = 5")
            cur.execute("DELETE FROM Instructor WHERE student_id = 5") # Delete records of the instructor existing.
            test_con.commit()

    def test_accept_proposal(self, client: FlaskClient) -> None:
        resp = client.put('proposals/1')
        self.assertStatus(resp, 200)
        with sqlite3.connect("test.db") as test_con:
            cur = test_con.cursor()
            cur.execute("SELECT * FROM Proposal WHERE proposal_id = 1")
            results = cur.fetchone()
            self.assertIsNone(results)
        resp2 = client.get('students/5')
        self.assertEqual(resp2.json['is_approved'], 1)  # Check if the student is approved.
        student = Student.fetch(5)
        self.assertEqual(student.advisor.advisor_id, 3)  # Check if the advisor was correctly set.


class TestProposalInvalidAccept(flask_unittest.ClientTestCase):

    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "advisortest@iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_accept_proposal_unathorized_advisor(self, client: FlaskClient) -> None:
        """
        Attempt to accept an unonwned proposal.
        """
        resp = client.put('proposals/1')
        self.assertStatus(resp, 403)

    def test_accept_proposal_nonexistent_advisor(self, client: FlaskClient) -> None:
        """
        Attempt to accept an proposal that does not exist.
        """
        resp = client.put('proposals/1000')
        self.assertStatus(resp, 404)


class TestProposalInvalidStudentAccept(flask_unittest.ClientTestCase):
    """
    Attempt to accept proposals with students, this is not allowed.
    """

    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "watson@std.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_accept_proposal_unathorized_student(self, client: FlaskClient) -> None:
        """
        Attempt to accept an unonwned proposal.
        """
        resp = client.put('proposals/1')
        self.assertStatus(resp, 403)

    def test_accept_proposal_nonexistent_student(self, client: FlaskClient) -> None:
        """
        Attempt to accept an proposal that does not exist.
        """
        resp = client.put('proposals/1000')
        self.assertStatus(resp, 403)  # But we should still get 403!


class TestPropose(flask_unittest.ClientTestCase):

    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "studenttest2@std.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.
        with sqlite3.connect("test.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Proposal WHERE student_id = 2")
            cur.execute("UPDATE Student SET has_proposed = FALSE WHERE student_id = 2")
            con.commit()

    def test_propose_to(self, client: FlaskClient) -> None:
        """
        Attempt to propose to a valid advisor.
        """
        resp = client.post('proposals', json={"advisor_id": 3})  # Let us propose to Bouwman.
        self.assertStatus(resp, 201)
        self.assertEqual(resp.json["student_id"], 2)
        self.assertEqual(resp.json["advisor_id"], 3)
        proposal_id = resp.json["proposal_id"]
        student = Student.fetch(2)
        self.assertEqual(student.has_proposed, True)  # Check if the student has proposed.
        advisor = Advisor.fetch(3)
        self.assertIn(proposal_id, [proposal.proposal_id for proposal in advisor.proposals])  # Check that the advisor got it.

    def test_propose_again(self, client: FlaskClient) -> None:
        """
        Attempt to propose twice, second one should fail.
        """

        resp = client.post('proposals', json={"advisor_id": 3})  # Let us propose to Bouwman.
        self.assertStatus(resp, 201)
        resp = client.post('proposals', json={"advisor_id": 1})  # This should fail.
        self.assertStatus(resp, 409)


class TestProposeAlreadyAdvisor(flask_unittest.ClientTestCase):
    """
    Attempt to propose with a student who already has an advisor.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "watson@std.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_propose_again(self, client: FlaskClient) -> None:
        """
        Attempt to propose, which should fail given we already have an advisor.
        """
        resp = client.post('proposals', json={"advisor_id": 1})  # This should fail.
        self.assertStatus(resp, 409)
