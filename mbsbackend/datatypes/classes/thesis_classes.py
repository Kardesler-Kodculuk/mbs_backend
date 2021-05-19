from mbsbackend.datatypes.database import bind_database
from dataclasses import dataclass
from typing import Optional, List


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
    dissertation_id: int
    jury_id: int
    evaluation: str

    @classmethod
    def get_consensus(cls, dissertation_id: int, member_count: int) -> str:
        """
        Get the consensus about the Thesis state of the student.

        :param dissertation_id: ID of the dissertation.
        :param member_count: Number of jury members in dissertations.
        :return The consensus of the dissertation.
        """
        evaluations: List[Evaluation] = Evaluation.fetch_where('dissertation_id', dissertation_id)
        decisions = {"Correction": 0, "Rejected": 0, "Approved": 0}
        for evaluation in evaluations:
            decisions[evaluation.evaluation] += 1
        if sum(decisions.values()) == member_count:
            items = decisions.items()
            items = list(items)
            items.sort(key=lambda item: item[1], reverse=True)
            return items[0][0]
        else:
            return "Undecided"
