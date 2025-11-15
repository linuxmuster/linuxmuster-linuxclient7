import ldap, ldap.sasl, sys, getpass, subprocess, pwd, os, os.path
from pathlib import Path
from linuxmusterLinuxclient7 import logging, constants, config, user, ldapHelper, shares, fileHelper, computer, localUserHelper

def readAttributes():
    """
    Reads all attributes of the current user from ldap

    :return: Tuple (success, dict of user attributes)
    :rtype: tuple
    """
    if not user.isInAD():
        return False, None

    return ldapHelper.searchOne(f"(sAMAccountName={user.username()})")

def school():
    """
    Gets the school of the current user from the AD

    :return: The short name of the school
    :rtype: str
    """
    rc, userdata = readAttributes()
    
    if not rc:
        return False, None

    return True, userdata["sophomorixSchoolname"]

def username():
    """
    Returns the user of the current user

    :return: The username of the current user
    :rtype: str
    """
    return getpass.getuser().lower()

def isUserInAD(user):
    """
    Checks if a given user is an AD user.

    :param user: The username of the user to check
    :type user: str
    :return: True if the user is in the AD, False if it is a local user
    :rtype: bool
    """
    if not computer.isInAD():
        return False
    
    rc, groups = localUserHelper.getGroupsOfLocalUser(user)
    if not rc:
        return False

    return "domain users" in groups

def isInAD():
    """Checks if the current user is an AD user.

    :return: True if the user is in the AD, False if it is a local user
    :rtype: bool
    """
    return isUserInAD(username())

def isRoot():
    """
    Checks if the current user is root

    :return: True if the current user is root, False otherwise
    :rtype: bool
    """
    return os.geteuid() == 0

def isInGroup(groupName):
    """
    Checks if the current user is part of a given group

    :param groupName: The name of the group
    :type groupName: str
    :return: True if the user is part of the group, False otherwise
    :rtype: bool
    """
    rc, groups = localUserHelper.getGroupsOfLocalUser(username())
    if not rc:
        return False

    return groupName in groups

def cleanTemplateUserGtkBookmarks():
    """Remove gtk bookmarks of the template user from the current users `~/.config/gtk-3.0/bookmarks` file.
    """
    logging.info("Cleaning {} gtk bookmarks".format(constants.templateUser))
    gtkBookmarksFile = constants.gtkBookmarksFile.format(user.username())
    if not os.path.isfile(gtkBookmarksFile):
        logging.warning("Gtk bookmarks file not found, skipping!")
        return False

    return fileHelper.removeLinesInFileContainingString(gtkBookmarksFile, constants.templateUser)

def getHomeShareMountpoint():
    """
    Returns the mountpoint of the users serverhome.

    :return: The monutpoint of the users serverhome
    :rtype: str
    """
    rc, homeShareName = _getHomeShareName()

    if rc:
        basePath = constants.shareMountBasepath.format(username())
        return True, f"{basePath}/{homeShareName}"

    return False, None

def mountHomeShare():
    """
    Mounts the serverhome of the current user

    :return: True on success, False otherwise
    :rtype: bool
    """
    rc1, userAttributes = readAttributes()
    rc2, shareName = _getHomeShareName(userAttributes)
    if rc1 and rc2:
        try:
            homeShareServerPath = userAttributes["homeDirectory"]
            res = shares.mountShare(homeShareServerPath, shareName=shareName, hiddenShare=False, username=username())
            return res

        except Exception as e:
            logging.error("Could not mount home dir of user")
            logging.exception(e)

    return False, None

# --------------------
# - Helper functions -
# --------------------

def _getHomeShareName(userAttributes=None):
    if userAttributes is None:
        rc, userAttributes = readAttributes()
    else:
        rc = True

    if rc:
        try:
            nameTemplate = config.shares()["nameTemplate"]
            letter = userAttributes['homeDrive'].replace(':', '')
            shareName = nameTemplate.format(label=username(), letter=letter)
            return True, shareName

        except Exception as e:
            # This happens when userAttributes does not contain homeDrive
            logging.error("Could not find home dir of user.")
            logging.exception(e)

    return False, None