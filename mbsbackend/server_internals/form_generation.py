"""
Holds functions to generate forms.
"""
from datetime import date
from functools import lru_cache
from uuid import uuid4
from docxtpl import DocxTemplate

from mbsbackend.external_services.obs_api import OBSApi


@lru_cache()  # Effectively turns this into a dictionary.
def get_template(form_name) -> DocxTemplate:
    """
    Given the form name, get the corresponding DocxTemplate.
    """
    return DocxTemplate(f'docx_templates/Form-{form_name}.docx')



def generate_from_template(context: dict, form_name: str) -> str:
    """
    Generate a form and save it to a file, return the filename.
    """
    template = get_template(form_name)
    template.render(context)
    file_name = uuid4().hex
    file_name = f'generated_forms/{file_name}.docx'
    template.save(file_name)
    return file_name


def generate_form_td(student) -> str:
    """
    Generate the Form TD and save it temporarily to somewhere,
        return the filename.
    """
    return generate_from_template({
        "student": student,
        "advisor": student.advisor,
        "obs_manager": OBSApi
    }, 'TD')


def generate_form_ts(student) -> str:
    """
    Generate form TS, Thesis Defense Exam Jury Report Form.
    """
    juries = student.dissertation.get_jury_members(student.student_id)
    date_ = date.fromtimestamp(student.dissertation.jury_date)
    return generate_from_template({
        'len': len,
        'date': date_,
        'juries': juries,
        'obs_manager': OBSApi,
        'student': student
    }, 'TS')


def generate_form_tj_a(student) -> str:
    """
    Generate form TJ-a.
    """
    return generate_from_template({
        "student": student,
        "obs_manager": OBSApi
    }, "TJ-a")

