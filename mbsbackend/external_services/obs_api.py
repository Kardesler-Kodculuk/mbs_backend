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
