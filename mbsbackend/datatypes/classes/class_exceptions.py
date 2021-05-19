class StudentAlreadyHasAdvisorException(Exception):
    """
    Raised when attempted to access recommended advisors
        of a student but the student already has an advisor.
    """
    pass


class InvalidUserClassException(Exception):
    """
    Raises when the attempted class is not a user class.
    """
    pass


class JuryMemberDoesNotExistException(Exception):
    """
    Raises when a jury member referred with their id does not
        exist.
    """
    pass


class InvalidStudentState(Exception):
    """
    Student is not in a valid state for this operation
        to happen.
    """
    pass
