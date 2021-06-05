import datetime
from time import strftime

from mbsbackend.datatypes.database import bind_database
from dataclasses import dataclass
from typing import Optional, List, Union
from .user_relationships import Proposal, Instructor, Recommended
from .thesis_classes import Defending, Member, Has, Thesis, Evaluation
from .class_exceptions import StudentAlreadyHasAdvisorException


@bind_database(obj_id_row='department_id')
@dataclass
class Department:
    """
    Represents a department such as Computer Engineering
    """
    department_id: int
    department_name: str
    turkish_department_name: str


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
        possibilities: List[type] = [Advisor, Student, DBR, Jury]
        for possibility in possibilities:
            if possibility.has(self.user_id):  # If user belongs to this class, we can fetch it.
                return possibility.fetch(self.user_id)

    @property
    def full_name(self) -> str:
        return self.name_ + ' ' + self.surname

    @property
    def department(self) -> Department:
        return Department.fetch(self.department_id)


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

    @property
    def jury_credentials(self) -> Optional["Jury"]:
        """
        Return Jury credentials of the Advisor if they exist,
            ie: If an advisor is also a Jury member. Otherwise
            return None.
        """
        if not Jury.has(self.advisor_id):
            return None
        return Jury.fetch(self.advisor_id)

    def can_evaluate(self, student: "Student") -> bool:
        """
        Check if Jury is member in any of this student's
            dissertations.
        """
        return self.advisor_id in student.dissertation_info['jury_ids']

    def create_jury(self) -> None:
        """
        Make the advisor a Jury member as well.
        """
        values = [self.advisor_id, False, "Izmir Institute of Technology",
                        "+90 5XX XXX XX XX", False]
        Jury.create_unique(values)


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

    @property
    def students(self) -> List[int]:
        if not Member.has_where('jury_id', self.jury_id):
            return []
        is_member_in: List[Member] = Member.fetch_where('jury_id', self.jury_id)
        defending_relationships = [Defending.fetch_where('dissertation_id', member.dissertation_id)[0]
                                   for member in is_member_in]
        return [defending_relationship.student_id for defending_relationship in defending_relationships]

    @classmethod
    def add_new_jury(cls, req, dep_id):
        user_args = [-1, req['name_'], req['surname'], "$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg", req['email'], dep_id]
        jury_args = [-1, False, req['institution'], req['phone_number'], True]
        user = User_(*user_args)
        user.create()
        jury_args[0] = user.user_id
        new_jury = Jury.create_unique(jury_args)
        return new_jury

    def can_evaluate(self, student: "Student") -> bool:
        """
        Check if Jury is member in any of this student's
            dissertations.
        """
        return self.jury_id in student.dissertation_info['jury_ids']


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
        recommendations: List[Recommended] = []
        if Recommended.has_where('student_id', self.student_id):  # If any recommendation available.
            # Add them to the list.
            recommendations.extend(Recommended.fetch_where('student_id', self.student_id))
        return recommendations  # Return the list.

    @property
    def is_advisors_recommended(self) -> bool:
        """
        Return true if a Student's advisors have been recommended.
        """
        return any((self.advisor, self.recommendations, self.proposals))

    @property
    def proposals(self) -> List[Proposal]:
        proposals: List[Proposal] = []
        if Proposal.has_where('student_id', self.student_id):
            proposals.extend(Proposal.fetch_where('student_id', self.student_id))
        return proposals

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

    @property
    def latest_thesis_name(self) -> str:
        """
        Generate thesis name from the filename.
        """
        latest_thesis: Thesis = Thesis.fetch(self.latest_thesis_id)
        file_name = latest_thesis.original_name
        name_proper, extension = file_name.split('.')
        name_capitalised_and_parsed = ' '.join(map(lambda str_: str_.capitalize(), name_proper.split('_')))
        return name_capitalised_and_parsed

    @property
    def dissertation_info(self) -> Optional[dict]:
        """
        Return Student's Dissertation information and
            the jury members in it.

        :return Information amount the dissertation and
            the jury member.
        """
        if not Defending.has_where('student_id', self.student_id):
            return None
        defending: Defending = Defending.fetch_where('student_id', self.student_id)[0]
        dissertation: Dissertation = Dissertation.fetch(defending.dissertation_id)
        dissertation_info = dissertation.get_info(self.student_id)
        return dissertation_info

    @property
    def dissertation(self) -> "Dissertation":
        return Dissertation.fetch(Defending.fetch_where('student_id', self.student_id)[0].dissertation_id)

    def create_dissertation_for(self, jury_members: List[int], dissertation_date: int) -> Optional["Dissertation"]:
        """
        Create a new dissertation for this student.
        :param jury_members: IDs of the jury members that shall defend this dissertation.
        :param dissertation_date: Date of the dissertation.
        :return the generated dissertation object or None if one jury member is not found.
        """
        if self.advisor.advisor_id not in jury_members:
            jury_members.append(self.advisor.advisor_id)
        if not all(Jury.has(jury_id) for jury_id in jury_members):
            return None
        new_dissertation = Dissertation(-1, dissertation_date, False)
        new_dissertation.create()
        for jury_id in jury_members:
            new_member = Member(-1, new_dissertation.dissertation_id, jury_id)
            new_member.create()
        defending = Defending(-1, new_dissertation.dissertation_id, self.student_id)
        defending.create()
        return new_dissertation


@bind_database(obj_id_row='dbr_id')
@dataclass
class DBR(User_):
    """
    Departmental Board Representative.
    """
    dbr_id: int

    @property
    def students(self) -> List[int]:
        if not Student.has_where('department_id', self.department_id):
            return []
        students = Student.fetch_where('department_id', self.department_id)
        return [student.user_id for student in students]

    @property
    def students_without_recommendations(self) -> List[int]:
        """
        Return a list of Student IDs of the Students that need a recommendation.
        """
        if not Student.has_where('department_id', self.department_id):
            return []
        students = Student.fetch_where('department_id', self.department_id)
        return [student.user_id for student in students if not student.is_advisors_recommended]

    @property
    def advisors(self) -> List[int]:
        if not Advisor.has_where('department_id', self.department_id):
            return []
        advisors = Advisor.fetch_where('department_id', self.department_id)
        return [advisor.user_id for advisor in advisors]


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
    is_approved: int  # TSS date and jury configuration must be approved first.

    def get_info(self, student_id) -> Optional[dict]:
        """
        Get info about dissertation.
        """
        if not Member.has_where('dissertation_id', self.dissertation_id):
            return None
        member_relationships: List[Member] = Member.fetch_where('dissertation_id', self.dissertation_id)
        jury_members: List["Jury"] = [Jury.fetch(member.jury_id) for member in member_relationships]
        jury_ids = [jury.jury_id for jury in jury_members]
        dissertation_info = {"jury_date": self.jury_date, "jury_ids": jury_ids, "student_id": student_id}
        if not self.is_approved:
            dissertation_info['status'] = 'Pending'
        else:
            dissertation_info['status'] = Evaluation.get_consensus(self.dissertation_id, len(jury_ids))
        return dissertation_info

    def delete_dissertation(self):
        """
        Delete a dissertation alongside with
            its associated objects.
        """
        defending = Defending.fetch_where('dissertation_id', self.dissertation_id)
        defending[0].delete()
        members = Member.fetch_where('dissertation_id', self.dissertation_id)
        for member in members:
            member.delete()
        self.delete()

    def get_jury_members(self, student_id: int) -> List[Jury]:
        dissertation_info = self.get_info(student_id)
        jury_members = [Jury.fetch(id_) for id_ in self.get_info(student_id)['jury_ids']]
        return jury_members

    @property
    def by_majority(self) -> bool:
        """
        Is the decision taken by majority.

        :return True if the Dissertation decision is taken by
             majority as opposed to by everyone in the group.
        """
        evaluations: List[Evaluation] = Evaluation.fetch_where('dissertation_id', self.dissertation_id)
        decisions = {"Correction": 0, "Rejected": 0, "Approved": 0}
        for evaluation in evaluations:
            decisions[evaluation.evaluation] += 1
        results = list(decisions.keys())
        results.sort(reverse=True)
        return results.pop(0) != len(evaluations)

    @property
    def formatted_date(self) -> str:
        return strftime("%d/%m/%Y", datetime.datetime.fromtimestamp(self.jury_date).timetuple())

    @property
    def formatted_time(self) -> str:
        return strftime("%H:%m", datetime.datetime.fromtimestamp(self.jury_date).timetuple())

