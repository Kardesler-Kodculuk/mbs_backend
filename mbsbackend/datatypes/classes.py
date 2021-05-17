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


@bind_database(obj_id_row='department_id')
@dataclass
class Department:
    """
    Represents a department such as Computer Engineering
    """
    department_id: int
    department_name: str


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


@bind_database(obj_id_row='recommendation_id')
@dataclass
class Recommended:
    """
    Indicates that an advisor was
        recommended to a student.
    """
    recommendation_id: int
    student_id: int
    advisor_id: int


@bind_database(obj_id_row='proposal_id')
@dataclass
class Proposal:
    """
    Indicates a student that has proposed
        to an advisor.
    """
    proposal_id: int
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
    department_id: int

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
    doctoral_specialty: str

    @property
    def proposals(self) -> List[Proposal]:
        proposals = []
        if Proposal.has_where('advisor_id', self.advisor_id):  # Check if any students proposed.
            proposals.extend(Proposal.fetch_where('advisor_id', self.advisor_id))  # Fetch them.
        return proposals

    def set_advisor_to(self, student: "Student") -> None:
        """
        Set this advisor to an advisor to a student.

        :param student: New advisee of the advisor.
        """
        instructor_relationship = Instructor(-1, student.student_id, self.advisor_id)
        instructor_relationship.create()
        student.is_approved = True
        student.update()  # Update the student's state.

    @property
    def students(self) -> List[int]:
        """
        Get a list of student ids managed by this advisor.
        """
        instructors = Instructor.fetch_where("advisor_id", self.advisor_id)  # Get Instructor entities.
        return [instructor.student_id for instructor in instructors]  # Get the student IDs from them.


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
    phone_number: str
    is_appointed: bool


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
    is_thesis_sent: bool

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
    def recommendations(self) -> List[Recommended]:
        if self.advisor:
            raise StudentAlreadyHasAdvisorException
        recommendations: List[Recommended] = []
        if Recommended.has_where('student_id', self.student_id):  # If any recommendation available.
            # Add them to the list.
            recommendations.extend(Recommended.fetch_where('student_id', self.student_id))
        return recommendations  # Return the list.

    @property
    def theses(self) -> List["Thesis"]:
        """
        Return the list of Theses uploaded by this
            Student user.
        """
        theses_ids: List[int] = []
        if Has.has_where('student_id', self.student_id):  # If the user has uploaded any theses' yet.
            theses_ids.extend([has_relationship.thesis_id
                               for has_relationship in Has.fetch_where('student_id', self.student_id)])
        return [Thesis.fetch(thesis_id) for thesis_id in theses_ids]

    @property
    def latest_thesis_id(self) -> int:
        theses_ = self.theses
        theses_.sort(key=lambda thesis: thesis.submission_date)
        theses_.reverse()
        if theses_:
            return theses_[0].thesis_id
        else:
            return -1

@bind_database(obj_id_row='thesis_id')
@dataclass
class Thesis:
    """
    Class holding data on a Master's
        Student's Thesis.
    """
    thesis_id: int
    file_path: str
    plagiarism_ratio: int
    thesis_topic: str
    submission_date: int


@bind_database(obj_id_row='dissertation_id')
@dataclass
class Dissertation:
    """
    Represents the exam done to evaluate whether or not if
        a thesis shall pass. Turkish for this term is Tez
        Savunma Sınavı.
    """
    dissertation_id: int
    jury_date: int
    is_approved: int # TSS date and jury configuration must be approved first.


@bind_database(obj_id_row='member_id')
@dataclass
class Member:
    """
    Represents the relationship between a jury member and a
        dissertation they evaluate on.
    """
    member_id: int
    dissertation_id: int
    jury_id: int


@bind_database(obj_id_row='defending_id')
@dataclass
class Defending:
    """
    Represents the relationship between a student and the dissertation
        their thesis is evaluated in.
    """
    defending_id: int
    dissertation_id: int
    student_id: int


@bind_database(obj_id_row='has_id')
@dataclass
class Has:
    """
    Represents who owns a thesis.
    """
    has_id: int
    thesis_id: int
    student_id: int


@bind_database(obj_id_row='evaluation_id')
@dataclass
class Evaluation:
    """
    Represents an evaluation by a jury member on
        a specific dissertation.
    """
    evaluation_id: int
    jury_id: int
    evaluation: str


@bind_database(obj_id_row='dbr_id')
@dataclass
class DBR:
    """
    Departmental Board Representative.
    """
    dbr_id: int
    department_id: int


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
