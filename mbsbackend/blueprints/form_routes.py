import os
from json import dumps
from typing import Dict, Callable

from flask import Blueprint, Response, send_file
from flask_jwt_extended import current_user, jwt_required

from mbsbackend.datatypes.classes.user_classes import Student, DBR
import mbsbackend.server_internals.form_generation as form_generation


form_functions: Dict[str, Callable] = {
    "TD": form_generation.generate_form_td,
    "TS": form_generation.generate_form_ts,
    "TJ-a": form_generation.generate_form_tj_a,
    'TJ': form_generation.generate_form_tj
}


def create_form_routes() -> Blueprint:
    form_blueprint = Blueprint('form_routes', __name__)

    @form_blueprint.route('/form/<student_id>/<form_id>')
    @jwt_required()
    def get_form(student_id: str, form_id: str) -> Response:
        """
        Given the form ID and the student ID, generate that form
            for this student and return it.
        """
        id_ = int(student_id)
        user = current_user
        dbr = user.downcast()
        if not isinstance(dbr, DBR):
            return Response(dumps({"msg": "Incorrect user type."}), mimetype='application/json', status=403)
        if not Student.has(id_):
            return Response(dumps({"msg": "Student id not found."}), mimetype='application/json', status=404)
        student = Student.fetch(id_)
        if form_id not in form_functions:
            return Response(dumps({"msg": "Form not found."}), mimetype="application/json", status=404)
        else:
            return send_file(os.path.join(os.getcwd(), form_functions[form_id](student)),
                             mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    return form_blueprint
