import subprocess
from linuxmusterLinuxclient7 import logging

def getGroupsOfLocalUser(username):
    """
    Get all groups of a local user

    :param username: The username of the user
    :type username: str
    :return: Tuple (success, list of groups)
    :rtype: tuple
    """
    try:
        groups = subprocess.check_output(["id", "-Gnz", username])
        stringList=[x.decode('utf-8') for x in groups.split(b"\x00")]
        return True, stringList
    except Exception as e:
        logging.warning("Exception when querying groups of user {}, it probaply does not exist".format(username))
        return False, None