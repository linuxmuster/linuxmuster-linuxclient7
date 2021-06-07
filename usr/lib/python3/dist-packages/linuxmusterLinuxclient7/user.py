import ldap, ldap.sasl, sys, getpass, subprocess, pwd, os, os.path
from pathlib import Path
from linuxmusterLinuxclient7 import logging, constants, config, user, ldapHelper, shares, fileHelper, computer, localUserHelper

def readAttributes():
    if not user.isInAD():
        return False, None

    return ldapHelper.searchOne("(sAMAccountName={})".format(user.username()))

def school():
    rc, userdata = readAttributes()
    
    if not rc:
        return False, None

    return True, userdata["sophomorixSchoolname"]

def username():
    return getpass.getuser()

def isUserInAD(user):
    if not computer.isInAD():
        return False
    
    rc, groups = localUserHelper.getGroupsOfLocalUser(user)
    if not rc:
        return False

    return "domain users" in groups

def isInAD():
    return isUserInAD(username())

def isRoot():
    return os.geteuid() == 0

def isInGroup(groupName):
    rc, groups = localUserHelper.getGroupsOfLocalUser(username())
    if not rc:
        return False

    return groupName in groups

def cleanTemplateUserGtkBookmarks():
    logging.info("Cleaning {} gtk bookmarks".format(constants.templateUser))
    gtkBookmarksFile = "/home/{0}/.config/gtk-3.0/bookmarks".format(user.username())

    if not os.path.isfile(gtkBookmarksFile):
        logging.warning("Gtk bookmarks file not found, skipping!")
        return

    fileHelper.removeLinesInFileContainingString(gtkBookmarksFile, constants.templateUser)

def getHomeShareMountpoint():
    rc, homeShareName = _getHomeShareName()

    if rc:
        basePath = constants.shareMountBasepath.format(username())
        return True, f"{basePath}/{homeShareName}"

    return False, None

def mountHomeShare():
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
            usernameString = username()
            shareName = f"{usernameString} ({userAttributes['homeDrive']})"
            return True, shareName

        except Exception as e:
            logging.error("Could not mount home dir of user")
            logging.exception(e)

    return False, None