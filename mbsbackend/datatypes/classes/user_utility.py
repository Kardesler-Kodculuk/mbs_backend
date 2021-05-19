from typing import Optional
from dataclasses import asdict
from .class_exceptions import InvalidUserClassException
from .user_classes import Student, Advisor, DBR, Jury, Department


def get_user(class_type: type, user_id: int) -> Optional[dict]:
    """
    Get a user's information excluding the password.

    :param class_type: Class of the user, student or advisor.
    :param user_id: ID of the user.
    :return The user information as a dictionary or None if no such user exists.
    """
    if class_type not in [Student, Advisor, DBR, Jury]:
        raise InvalidUserClassException
    if not class_type.has(user_id):
        return None
    user_ = class_type.fetch(user_id)
    dict_ = asdict(user_)  # Get the user information as a dictionary.
    if class_type == Student:
        dict_['latest_thesis_id'] = user_.latest_thesis_id
    del dict_['password']  # Delete password information.
    convert_department(dict_)
    return dict_


def convert_department(user_dict: dict) -> None:
    """
    Given a user dataclass' dictionary representation,
        convert the department_id field to department
        and its key to the name of the department.
    """
    department_id = user_dict['department_id']
    department_name = Department.fetch(int(department_id)).department_name
    del user_dict['department_id']
    user_dict['department'] = department_name
