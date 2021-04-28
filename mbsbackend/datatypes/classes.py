from dataclasses import dataclass
from enum import Enum
from typing import List, Union
from datetime import date
from typing import List
from .database import bind_database


class PageType(Enum):
    """
    This enum holds the main pages
        this user is allowed to view.
    """
    STUDENT_MANAGEMENT = "STUDENT_MANAGEMENT"
    PPF_MANAGEMENT = "PPF_MANAGEMENT"
    THESIS_MANAGEMENT = "THESIS_MANAGEMENT"
    ADVISOR_SELECTION = "ADVISOR_SELECTION"


@bind_database(obj_id_row='user_id')
@dataclass
class User_:
    """
    Base class that is used for all
        user types.
    """
    user_id: int
    name_: str
    surname: str
    password: str  # Hashed password string.
    email: str

    def downcast(self) -> Union["Advisor", "Student"]:
        """
        Downcast the user object to one of its subtypes.

        :param user: A variable of type user.
        :return the downcasted object.
        """
        possibilities: List[type] = [Advisor, Student]
        for possibility in possibilities:
            if possibility.has(self.user_id):  # If user belongs to this class, we can fetch it.
                return possibility.fetch(self.user_id)


@bind_database(obj_id_row='advisor_id')
@dataclass
class Advisor(User_):
    """
    Class holding data on users with
        advisor privileges.
    """
    advisor_id: int
    department: str
    doctoral_specialty: str


@bind_database(obj_id_row='jury_id')
@dataclass
class Jury(User_):
    """
    Class holding data on users
        with Jury privileges.
    """
    jury_id: int
    is_approved: bool
    institution: str
    is_appointed: bool
    department: str


@bind_database(obj_id_row='student_id')
@dataclass
class Student(User_):
    """
    Class holding data on users
        with Student privileges.
    """
    student_id: int
    is_approved: bool
    semester: int
    program_name: str
    thesis_topic: str
    graduation_status: str

    @property
    def advisor(self) -> Advisor:
        return None


@bind_database(obj_id_row='thesis_id')
@dataclass
class Thesis:
    """
    Class holding data on a Master's
        Student's Thesis.
    """
    thesis_id: int
    file_path: str
    evaluation: str
    is_final: bool
    thesis_topic: str
    due_date: date
    submission_date: date
    extension_status: str 
    extension_info: str


