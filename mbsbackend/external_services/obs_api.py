class OBSApi:

    @staticmethod
    def get_student_id(student_email: str) -> str:
        """
        Given a student's email return their student
            ID.
        """
        character_ascii = [str(ord(char_)) for char_ in student_email]
        student_number = ''.join(character_ascii)
        return student_number[:8]

    """
    Below are some mock functions, these check student's credit
        requirements.
    """

    @staticmethod
    def took_classes(student_email: str) -> bool:
        return True

    @staticmethod
    def completed_credit(student_email: str) -> bool:
        return True

    @staticmethod
    def check_gpa(student_email: str) -> bool:
        return True

    @staticmethod
    def correct_grading(student_email: str) -> bool:
        return True

    @staticmethod
    def check_requirements(student_email: str) -> bool:
        return True
