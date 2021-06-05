import os
import sqlite3
from os import environ
from os.path import exists
import flask_unittest
from hashlib import md5
from flask.testing import FlaskClient
from tests.expected_responses import expected_pdf_file_name, expected_theses_list, expected_thesis_metadata_get, \
    expected_pdf_upload_resp, expected_sparrowhawk

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
        resp = client.get('/theses/metadata/0')
        self.assertStatus(resp, 200)
        self.assertDictEqual(resp.json, expected_thesis_metadata_get)

    def test_get_thesis_metadata_fail(self, client: FlaskClient) -> None:
        """
        Attempt to get a nonexistent thesis' metadata.
        """
        resp = client.get('/theses/metadata/10000')
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


class TestUploadThesis(flask_unittest.ClientTestCase):
    """
    Test if a student upload a new thesis file.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "grey@std.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.
        with sqlite3.connect('test.db') as db:
            cur = db.cursor()
            cur.execute("SELECT thesis_id, file_path FROM Thesis WHERE original_name = 'grey_thesis_upload_example.pdf'")
            thesis_id, path_ = cur.fetchone()
            cur.execute(f"DELETE FROM Thesis WHERE thesis_id = {thesis_id}")
            cur.execute(f"DELETE FROM Has WHERE thesis_id = {thesis_id}")
            db.commit()
        os.remove(path_)

    def test_upload_thesis(self, client: FlaskClient) -> None:
        """
        Check if the student can upload a thesis.
        """
        data = {}
        original_files = os.listdir('theses/')  # Get the names of the original files.
        with open('tests/example_pdfs/grey_thesis_upload_example.pdf', 'rb') as fp:
            data['file'] = (fp, 'grey_thesis_upload_example.pdf')
            resp = client.post('/theses', content_type='multipart/form-data', data=data)  # We are expecting a list of thesis ids.
        with open('tests/example_pdfs/grey_thesis_upload_example.pdf', 'rb') as fp:
            expected_hash = md5(fp.read()).digest()
        self.assertStatus(resp, 201)
        new_files = [file_name for file_name in os.listdir('theses') if file_name not in original_files]
        self.assertTrue(new_files)  # Make sure this is not empty.
        new_file = new_files[0]
        with open('theses/' + new_file, 'rb') as fp:
            actual_hash = md5(fp.read()).digest()
        self.assertEqual(actual_hash, expected_hash)
        json_response = resp.json
        self.assertNotEqual(json_response['thesis_id'], -1)  # To check if correct id is assigned.
        self.assertEqual(json_response['thesis_topic'], expected_pdf_upload_resp['thesis_topic'])


class TestDeleteThesis(flask_unittest.ClientTestCase):
    """
    Test if a student can delete an existing thesis file.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "grey@std.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_delete_thesis(self, client: FlaskClient) -> None:
        """
        Check if the student can delete a thesis.
        """
        data = {}
        with open('tests/example_pdfs/grey_thesis_delete_example.pdf', 'rb') as fp:
            data['file'] = (fp, 'grey_thesis_delete_example.pdf')
            resp = client.post('/theses', content_type='multipart/form-data', data=data)  # We are expecting a list of thesis ids.
        json_response = resp.json
        thesis_id = json_response['thesis_id']
        with sqlite3.connect('test.db') as db:
            cur = db.cursor()
            cur.execute(f"SELECT file_path FROM Thesis WHERE thesis_id = {thesis_id}")
            file_path = cur.fetchone()[0]
        resp = client.delete(f'/theses/{thesis_id}')
        self.assertStatus(resp, 204)
        self.assertFalse(exists(file_path), "File not properly deleted.")
        with sqlite3.connect('test.db') as db:
            cur = db.cursor()
            cur.execute(f"SELECT * FROM Thesis WHERE thesis_id = {thesis_id}")
            self.assertIsNone(cur.fetchone())
            cur.execute(f"SELECT * FROM Has WHERE thesis_id = {thesis_id}")
            self.assertIsNone(cur.fetchone())


class TestLatestThesisID(flask_unittest.ClientTestCase):
    """
    Test if the student's latest_thesis_id field is functioning correctly.
    """
    app = create_app()

    def setUp(self, client: FlaskClient) -> None:
        client.post('/jwt', json={"username": "grey@std.iyte.edu.tr", "password": "test+7348"})
        self.maxDiff = None

    def tearDown(self, client: FlaskClient) -> None:
        client.delete('/jwt')  # Logout.

    def test_latest_thesis_id(self, client: FlaskClient) -> None:
        student_info = client.get('/users').json['student']
        self.assertEqual(student_info['latest_thesis_id'], 1)
        data = {}  # Upload to see change.
        with open('tests/example_pdfs/grey_thesis_delete_example.pdf', 'rb') as fp:
            data['file'] = (fp, 'grey_thesis_delete_example.pdf')
            resp = client.post('/theses', content_type='multipart/form-data',
                               data=data)  # We are expecting a list of thesis ids.
        json_response = resp.json
        thesis_id = json_response['thesis_id']
        student_info = client.get('/users').json['student']
        self.assertEqual(student_info['latest_thesis_id'], thesis_id)  # Check if the thesis id changed.
        resp = client.delete(f'/theses/{thesis_id}')
        student_info = client.get('/users').json['student']
        self.assertEqual(student_info['latest_thesis_id'], 1)  # Now it should be back to 1.
