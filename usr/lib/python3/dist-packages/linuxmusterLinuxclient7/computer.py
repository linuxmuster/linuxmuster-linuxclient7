import socket
from linuxmusterLinuxclient7 import logging, ldapHelper, realm

def hostname():
    return socket.gethostname().split('.', 1)[0]

def readAttributes():
    return ldapHelper.searchOne("(sAMAccountName={}$)".format(hostname()))

def isInGroup(groupName):
    rc, userAdObject = readAttributes()
    if not rc:
        logging.error("Could not read computer AD Object!")
        return False

    return ldapHelper.isObjectInGroup(userAdObject["distinguishedName"], groupName)

def isInAD():
    return realm.isJoined()