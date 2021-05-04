import ldap, ldap.sasl, sys, getpass, subprocess, pwd, os, os.path
from linuxmusterLinuxclient7 import logging, constants, config, user, ldapHelper, shares, fileHelper, computer

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
    
    try:
        userDetails = str(subprocess.check_output(["id", "{}".format(user)]))

        if "(domain users)" in userDetails:
            return True
        else:
            return False
    except:
        logging.warning("Exception when querying user {}".format(user))
        return False

def isInAD():
    return isUserInAD(username())

def isRoot():
    return os.geteuid() == 0

def isInGroup(groupName):
    rc, userAdObject = readAttributes()
    if not rc:
        logging.error("Could not read user AD Object!")
        return False

    return ldapHelper.isObjectInGroup(userAdObject["distinguishedName"], groupName)

def cleanTemplateUserGtkBookmarks():
    logging.info("Cleaning {} gtk bookmarks".format(constants.templateUser))
    gtkBookmarksFile = "/home/{0}/.config/gtk-3.0/bookmarks".format(user.username())

    if not os.path.isfile(gtkBookmarksFile):
        logging.warning("Gtk bookmarks file not found, skipping!")
        return

    fileHelper.removeLinesInFileContainingString(gtkBookmarksFile, constants.templateUser)

def mountHomeShare():
    rc, userAttributes = readAttributes()
    if rc:
        # Try to mount home share!
        try:
            homeShareServerPath = userAttributes["homeDirectory"]
            username = userAttributes["sAMAccountName"]
            shares.mountShare(homeShareServerPath, shareName=username, hiddenShare=False, username=username)
        except Exception as e:
            logging.error("Could not mount home dir of user")
            logging.exception(e)