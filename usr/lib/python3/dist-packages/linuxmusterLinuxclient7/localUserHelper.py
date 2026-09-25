import subprocess
from linuxmusterLinuxclient7 import logging

_groupCache = {}

def getGroupsOfLocalUser(username):
    """
    Get all groups of a local user

    :param username: The username of the user
    :type username: str
    :return: Tuple (success, list of groups)
    :rtype: tuple
    """
    if username in _groupCache:
        return True, _groupCache[username]

    try:
        groups = subprocess.check_output(["id", "-Gnz", username])
        stringList=[x.decode('utf-8') for x in groups.split(b"\x00")]
        _groupCache[username] = stringList
        return True, stringList
    except Exception as e:
        logging.warning(f"Exception when querying groups of user {username}, it probably does not exist")
        return False, None