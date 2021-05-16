from hashlib import md5

class PlagiarismManager:
    """
    A mock plagiarism manager.
    """
    def __init__(self):
        pass

    def get_plagiarism_ratio(self, filepath):
        """
        A function that returns the same value for the same
            filepath, normally this would return the ratio of plagiarism.
        """
        return round(sum(md5(filepath.encode('ascii')).digest()) / 100)
