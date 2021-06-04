from os import environ
from sqlite3 import connect

import flask_unittest
from flask.testing import FlaskClient

from tests.expected_responses import advisors_list, recommended_advisors, students_without_recommendations

environ['FLASK_DB_NAME'] = 'test.db'  # This must be set before first importing the backend itself.
from mbsbackend import create_app


class TestDBRGet(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "welman@pers.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_get_advisors(self, client: FlaskClient) -> None:
        """
        Get all the advisors in a department as DBR.
        """
        resp = client.get('/advisors')
        self.assertStatus(resp, 200)
        self.assertCountEqual(resp.json['advisors'], advisors_list['advisors'])

    def test_get_recommendations(self, client: FlaskClient) -> None:
        """
        Get recommendations of a specific user as DBR.
        """
        resp = client.get('/recommendations/2')
        self.assertStatus(resp, 200)
        self.assertCountEqual(resp.json['recommended_advisors'], recommended_advisors['recommended_advisors'])


class TestDBRAddRecommendation(flask_unittest.ClientTestCase):
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "welman@pers.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.
        with connect('test.db') as db:
            cur = db.cursor()
            cur.execute('DELETE FROM Recommended WHERE advisor_id = 6 AND student_id = 2')
            db.commit()

    def test_add_recommendation(self, client: FlaskClient) -> None:
        """
        Add a new recommendation for a student.
        """
        resp = client.post('/recommendations/2', json={'advisor_id': 6})
        self.assertStatus(resp, 201)
        resp = client.get('/recommendations/2')
        expected_advisors_now = recommended_advisors['recommended_advisors'].copy()
        expected_advisors_now.append(6)
        self.assertCountEqual(resp.json['recommended_advisors'], expected_advisors_now)


class TestDBRRecommendationsFail(flask_unittest.ClientTestCase):
    """
    Test if DBR's different fail conditions work.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "lord@pers.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_add_recommendation_fail(self, client: FlaskClient) -> None:
        """
        Add a new recommendation for a student, fails because different department.
        """
        resp = client.post('/recommendations/2', json={'advisor_id': 6})
        self.assertEqual(resp.status_code, 403)

    def test_get_recommendation_fail(self, client: FlaskClient) -> None:
        """
        Attempt to get the recommendations of a student, fails because different department.
        """
        resp = client.get('/recommendations/2')
        self.assertEqual(resp.status_code, 403)

    def test_get_students_without_recommendations(self, client: FlaskClient) -> None:
        """
        And now for something completely different: Get a list of students without recommendations.
        This is here because lord@pers.iyte.edu.tr is the history advisor so.
        """
        resp = client.get('/recommendations/needed')
        self.assertStatus(resp, 200)
        self.assertDictEqual(students_without_recommendations, resp.json)
