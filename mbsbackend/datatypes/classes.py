from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Union, Optional
from datetime import date
from typing import List
from .database import bind_database


class StudentAlreadyHasAdvisorException(Exception):
    """
    Raised when attempted to access recommended advisors
        of a student but the student already has an advisor.
    """
    pass


class InvalidUserClassException(Exception):
    """
    Raised when the attempted class is not a user class.
    """
    pass


@bind_database(obj_id_row='id_')
@dataclass
class Instructor:
    """
    Indicates instructor relationship
        between a student and their
        advisor.
    """
    id_: int
    student_id: int
    advisor_id: int


@bind_database(obj_id_row='id_')
@dataclass
class Recommended:
    """
    Indicates that an advisor was
        recommended to a student.
    """
    id_: int
    student_id: int
    advisor_id: int

@bind_database(obj_id_row='id_')
@dataclass
class Proposal:
    """
    Indicates a student that has proposed
        to an advisor.
    """
    id_: int
    student_id: int
    advisor_id: int


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

    @property
    def proposals(self) -> List["Student"]:
        students = []
        if Proposal.has_where('advisor_id', self.advisor_id):  # Check if any students proposed.
            students.extend(*Proposal.fetch_where('advisor_id', self.advisor_id))  # Fetch them.
        return students


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
    has_proposed: bool
    semester: int
    program_name: str
    thesis_topic: str
    graduation_status: str
    jury_tss_decision: str

    @property
    def advisor(self) -> Optional[Advisor]:
        """
        Check if the student has an advisor,
            if they have return that advisor,
            otherwise return None.
        """
        if Instructor.has_where('student_id', self.student_id):  # Checks if the relationship exists.
            return Advisor.fetch(Instructor.fetch_where('student_id', self.student_id)[0].advisor_id)
        return None  # Otherwise return None.

    @property
    def recommendations(self) -> List[Advisor]:
        if self.advisor:
            raise StudentAlreadyHasAdvisorException
        recommendations: List[Advisor] = []
        if Recommended.has_where('student_id', self.student_id):  # If any recommendation available.
            # Add them to the list.
            recommendations.extend(*Recommended.fetch_where('student_id', self.student_id))
        return recommendations  # Return the list.


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


def get_user(class_type: type, user_id: int) -> Optional[dict]:
    """
    Get a user's information excluding the password.

    :param class_type: Class of the user, student or advisor.
    :param user_id: ID of the user.
    :return The user information as a dictionary or None if no such user exists.
    """
    if class_type not in [Student, Advisor]:
        raise InvalidUserClassException
    if not class_type.has(user_id):
        return None
    user_ = class_type.fetch(user_id)
    dict_ = asdict(user_)  # Get the user information as a dictionary.
    del dict_['password']  # Delete password information.
    return dict_


