"""
Holds functions to generate forms.
"""
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


def generate_form_td(student) -> str:
    """
    Generate the Form TD and save it temporarily to somewhere,
        return the filename.
    """
    template = get_template('TD')
    context = {
        "student": student,
        "advisor": student.advisor,
        "obs_manager": OBSApi
    }
    template.render(context)
    file_name = uuid4().hex
    file_name = f'generated_forms/{file_name}.docx'
    template.save(file_name)
    return file_name
