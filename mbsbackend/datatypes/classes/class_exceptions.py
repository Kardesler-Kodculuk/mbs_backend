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
