import os
import pwd

def get_user_context():
    """
    Returns a dictionary containing:
      - user_home: the home directory of the sudoer user
      - uid: the user ID of the sudoer user
      - gid: the group ID of the sudoer user
    """
    sudo_user = os.getenv("SUDO_USER")
    user_home = os.environ.get("USER_HOME")
    if not user_home:
        if sudo_user:
            user_info = pwd.getpwnam(sudo_user)
            user_home = user_info.pw_dir
            uid = user_info.pw_uid
            gid = user_info.pw_gid
        else:
            user_home = os.path.expanduser("~")
            uid, gid = os.getuid(), os.getgid()
    else:
        if sudo_user:
            user_info = pwd.getpwnam(sudo_user)
            uid = user_info.pw_uid
            gid = user_info.pw_gid
        else:
            uid, gid = os.getuid(), os.getgid()
    return {"user_home": user_home, "uid": uid, "gid": gid}

# Global value object for the sudoer user's context
USER_CONTEXT = get_user_context()
