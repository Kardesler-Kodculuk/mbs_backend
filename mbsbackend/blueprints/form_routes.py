from json import dumps
from typing import Dict, Callable

from flask import Blueprint, Response
from flask_jwt_extended import current_user

from mbsbackend.datatypes.classes.user_classes import Student, DBR
import mbsbackend.server_internals.form_generation as form_generation


form_functions: Dict[str, Callable] = {
    "TD": form_generation.generate_form_td
}

def create_form_routes() -> Blueprint:
    form_blueprint = Blueprint('form_routes', __name__)

    @form_blueprint.route('/form/<student_id>/<form_id>')
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
            return form_functions[form_id](student)

    return form_blueprint