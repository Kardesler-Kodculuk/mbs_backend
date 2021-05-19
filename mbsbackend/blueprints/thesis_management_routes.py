import os.path
import time
from json import dumps
from os import remove
from typing import Tuple, Union
from flask import Blueprint, request, Response, send_file
from flask_jwt_extended import jwt_required, current_user
from dataclasses import asdict

from werkzeug.utils import secure_filename

from mbsbackend.datatypes.classes.user_classes import Student
from mbsbackend.datatypes.classes.thesis_classes import Thesis, Has
from mbsbackend.external_services.plagiarism_api import PlagiarismManager
from mbsbackend.server_internals.verification import returns_json


def create_thesis_management_routes(plagiarism_api: PlagiarismManager) -> Blueprint:

    thesis_management_routes = Blueprint('thesis_management', __name__)

    @thesis_management_routes.route('/theses', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_student_theses() -> Tuple[Union[list, dict], int]:
        """
        Get a list of Theses uploaded so far by a student.
        """
        student = current_user.downcast()
        if not isinstance(student, Student):
            return {"msg": "Not authorised for this action."}, 403
        theses = student.theses
        return [thesis.thesis_id for thesis in theses], 200

    @thesis_management_routes.route('/theses/<thesis_id>/metadata', methods=['GET'])
    @returns_json
    @jwt_required()
    def get_thesis_metadata(thesis_id) -> Tuple[dict, int]:
        """
        Get metadata about a specific thesis.
        """
        thesis_id = int(thesis_id)
        if not Thesis.has(thesis_id):
            return {"msg": "Thesis not found."}, 404
        # TODO: If there is time we should check further for user's identity as well.
        thesis = Thesis.fetch(thesis_id)
        thesis_info = asdict(thesis)
        del thesis_info['file_path']  # It is better if the user is unaware of this.
        return thesis_info, 200

    @thesis_management_routes.route('/theses/<thesis_id>', methods=['GET'])
    @jwt_required()
    def get_thesis_file(thesis_id) -> Response:
        """
        Get the actual file of the thesis that is requested.
        """
        thesis_id = int(thesis_id)
        if not Thesis.has(thesis_id):
            return Response(dumps({"msg": "Thesis not found."}), status=404, mimetype='application/json')
        # TODO: If there is time we should check further for user's identity as well.
        thesis = Thesis.fetch(thesis_id)
        thesis_info = asdict(thesis)
        thesis_path = thesis_info['file_path']  # It is better if the user is unaware of this.
        return send_file(os.path.join(os.getcwd(), thesis_path), mimetype='application/pdf')

    @thesis_management_routes.route('/theses/<thesis_id>', methods=['DELETE'])
    @returns_json
    @jwt_required()
    def delete_thesis(thesis_id) -> Tuple[dict, int]:
        """
        Delete the thesis and associated metadata.
        """
        thesis_id = int(thesis_id)
        student = current_user.downcast()
        if not isinstance(student, Student):
            return {"msg": "Not authorised for this action."}, 403
        theses = student.theses  # TODO: If there is time we should check further for user's identity as well.
        if thesis_id not in [thesis.thesis_id for thesis in theses]:
            return {"msg": "Users cannot delete theses they do not own."}, 403
        thesis = Thesis.fetch(thesis_id)
        remove(os.path.join(os.getcwd(), thesis.file_path))  # Remove the thesis
        has_relationship = Has.fetch_where('thesis_id', thesis.thesis_id)[0]
        has_relationship.delete()  # Delete the ownership relationship
        thesis.delete()  # Delete the associated metadata.
        return {"msg": "Deleted thesis."}, 204

    @thesis_management_routes.route('/theses', methods=['POST'])
    @returns_json
    @jwt_required()
    def upload_thesis() -> Tuple[dict, int]:
        """
        Post a thesis to the system and return its metadata.
        """
        student = current_user.downcast()
        if not isinstance(student, Student):
            return {"msg": "Not authorised for this action."}, 403
        elif 'file' not in request.files:
            return {"msg": "Files must contain a file with key file."}, 400
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(os.getcwd(), 'theses/', filename))  # Save to theses directory.
        file_path = os.path.join('theses/', filename)  # Relative file path.
        new_thesis_metadata = Thesis(-1, file_path, plagiarism_api.get_plagiarism_ratio(file_path),
                                     student.thesis_topic, round(time.time()))
        new_thesis_metadata.create()
        new_ownership = Has(-1, new_thesis_metadata.thesis_id, student.student_id)
        new_ownership.create()
        metadata = asdict(new_thesis_metadata)
        del metadata['file_path']
        return metadata, 201

    return thesis_management_routes
