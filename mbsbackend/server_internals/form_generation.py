"""
Holds functions to generate forms.
"""
from uuid import uuid4


def generate_form_td(student) -> str:
    """
    Generate the Form TD and save it temporarily to somewhere,
        return the filename.
    """
