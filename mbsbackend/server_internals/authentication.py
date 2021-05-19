from typing import Optional, List
from passlib.hash import pbkdf2_sha256
from mbsbackend.datatypes.classes.user_classes import User_


def _authenticate_password(user_input: str, hash_: str) -> bool:
    """
    Check if the given user password is correct when compared
        to the hash. The hash is gotten from the database.

    :param user_input: Input user gave as password.
    :param hash_: Hash stored in the database.
    :return True if the password is correct.
    """
    return pbkdf2_sha256.verify(user_input, hash_)


def authenticate(username, password) -> Optional[User_]:
    """
    Attempt to authenticate a user.

    :param username: Username of the user.
    :param password: Password of the user.
    """
    user: List[User_] = User_.fetch_where("email", username)  # MBS uses email as the username.
    if user and _authenticate_password(password, user[0].password):  # If the password is confirmed
        return user[0]  # Return the user.


def identity(payload) -> User_:
    """
    Get the user from the decrypted JWT payload.

    :param payload: Payload from the decrypted JWT.
    :return User object in the JWT.
    """
    user_id = payload['identity']
    return User_.fetch(user_id)
