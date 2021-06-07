import socket
from linuxmusterLinuxclient7 import logging, ldapHelper, realm, localUserHelper

def hostname():
    return socket.gethostname().split('.', 1)[0]

def krbHostName():
    return hostname().upper() + "$"

def readAttributes():
    return ldapHelper.searchOne("(sAMAccountName={}$)".format(hostname()))

def isInGroup(groupName):
    rc, groups = localUserHelper.getGroupsOfLocalUser(krbHostName())
    if not rc:
        return False

    return groupName in groups

def isInAD():
    rc, groups = localUserHelper.getGroupsOfLocalUser(krbHostName())
    if not rc:
        return False

    return "domain computers" in groups