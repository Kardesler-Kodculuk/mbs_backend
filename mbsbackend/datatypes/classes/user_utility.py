from typing import Optional
from dataclasses import asdict
from .class_exceptions import InvalidUserClassException
from .user_classes import Student, Advisor, DBR, Jury, Department, User_


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
        dict_['is_advisors_recommended'] = any((user_.advisor, user_.recommendations, user_.proposals))
        dict_['has_dissertation'] = user_.dissertation_info is not None
    elif class_type == Advisor:
        dict_['is_jury'] = user_.jury_credentials is not None
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


def get_role_name(user: User_) -> str:
    if any(isinstance(user, class_) for class_ in (Advisor, Jury, Student)):
        return {Advisor: 'advisor', Jury: 'jury', Student: 'student'}[user.__class__]
        # It is actually impossible to do this using user.__class__.__name__ since that is overwritten
        # by the bind_database decorator.
    else:  # Otherwise must be DBR.
        return 'DBR'
