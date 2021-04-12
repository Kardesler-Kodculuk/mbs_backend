from dataclasses import dataclass
from enum import Enum
from datetime import date


class PageType(Enum):
    """
    This enum holds the main pages
        this user is allowed to view.
    """
    STUDENT_MANAGEMENT = "STUDENT_MANAGEMENT"
    PPF_MANAGEMENT = "PPF_MANAGEMENT"
    THESIS_MANAGEMENT = "THESIS_MANAGEMENT"
    ADVISOR_SELECTION = "ADVISOR_SELECTION"


@dataclass
class User:
    """
    Base class that is used for all
        user types.
    """
    user_id: int
    name: str
    surname: str
    password: str  # Hashed password string.
    email: str
    phone_number: str
    allowed_pages: list[str]


@dataclass
class Advisor(User):
    """
    Class holding data on users with
        advisor privileges.
    """
    department: str
    doctoral_specialty: str


@dataclass
class Jury(User):
    """
    Class holding data on users
        with Jury privileges.
    """
    is_approved: bool
    institution: str
    is_appointed: bool
    department: str


@dataclass
class Student(User):
    """
    Class holding data on users
        with Student privileges.
    """
    is_approved: bool
    semester: int
    program_name: str
    thesis_topic: str
    graduation_status: str
    jury_tss_decision: str


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
