import getpass
import os


class LoginUserNotFoundException(Exception):
    """
    Cannot find the login user
    """
    pass


def get_login_user(default_login=None):
    msg = "Cannot get the login user."
    try:
        login_user = getpass.getuser()
    except Exception as e:
        login_user = None
        msg = f'{msg}: {str(e)}'

    if login_user is None and default_login is not None:
        login_user = default_login

    if not login_user:
        raise LoginUserNotFoundException(msg)

    return login_user
