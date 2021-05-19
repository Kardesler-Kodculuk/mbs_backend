from mbsbackend.datatypes.database import bind_database
from dataclasses import dataclass


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
