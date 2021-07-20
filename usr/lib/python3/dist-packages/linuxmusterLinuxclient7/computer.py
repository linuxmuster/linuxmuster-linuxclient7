import socket
from linuxmusterLinuxclient7 import logging, ldapHelper, realm, localUserHelper

def hostname():
    """
    Get the hostname of the computer

    :return: The hostname
    :rtype: str
    """
    return socket.gethostname().split('.', 1)[0]

def krbHostName():
    """
    Get the krb hostname, eg. `COMPUTER01$`

    :return: The krb hostname
    :rtype: str
    """
    return hostname().upper() + "$"

def readAttributes():
    """
    Read all ldap attributes of the cumputer

    :return: Tuple (success, dict of attributes)
    :rtype: tuple
    """
    return ldapHelper.searchOne("(sAMAccountName={}$)".format(hostname()))

def isInGroup(groupName):
    """
    Check if the computer is part of an ldap group

    :param groupName: The name of the group to check
    :type grouName: str
    :return: True or False
    :rtype: bool
    """
    rc, groups = localUserHelper.getGroupsOfLocalUser(krbHostName())
    if not rc:
        return False

    return groupName in groups

def isInAD():
    """
    Check if the computer is joined to an AD

    :return: True or False
    :rtype: bool
    """
    rc, groups = localUserHelper.getGroupsOfLocalUser(krbHostName())
    if not rc:
        return False

    return "domain computers" in groups