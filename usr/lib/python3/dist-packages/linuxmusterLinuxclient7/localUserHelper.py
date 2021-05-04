import subprocess
from linuxmusterLinuxclient7 import logging

def getGroupsOfLocalUser(username):
    try:
        groups = subprocess.check_output(["id", "-Gnz", username])
        stringList=[x.decode('utf-8') for x in groups.split(b"\x00")]
        return True, stringList
    except Exception as e:
        logging.warning("Exception when querying groups of user {}, it probaply does not exist".format(username))
        return False, None