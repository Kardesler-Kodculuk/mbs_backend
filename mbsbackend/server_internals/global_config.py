"""
A singleton class that holds configuration variables
    independent from Flask.
"""


class Singleton(type):
    """
    A metaclass that turns classes deriving from it into
    Singleton classes, only one class can derive from this
    variation for the sake of simplicity.

    IN CASE THIS TRIGERS PLAGIARISM CHECK ON https://github.com/ambertide/ChangelingServer
    that is also me!

    Modified version of: https://stackoverflow.com/a/6798042/6663851
    """
    instance: "Singleton" = None

    def __call__(cls, *args, **kwargs) -> "Singleton":
        if cls.instance is None: # If it hasn't been created yet.
            cls.instance = super(Singleton, cls).__call__() # Create it.
        return cls.instance


class GlobalConfig(metaclass=Singleton):
    def __init__(self):
        self.testing = False
