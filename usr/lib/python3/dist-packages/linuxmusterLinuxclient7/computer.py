import socket, os, subprocess
from linuxmusterLinuxclient7 import logging, constants, ldapHelper, realm, localUserHelper

def hostname():
    """
    Get the hostname of the computer

    :return: The hostname
    :rtype: str
    """
    return socket.gethostname().split('.', 1)[0]

def hostnameIsValid():
    """
    Check if the hostname can be used as a computer account name in the AD (max. 15 characters)

    :return: True or False
    :rtype: bool
    """
    return len(hostname()) <= constants.maxHostnameLength

def checkHostname():
    """
    Check if the hostname is valid. If not, an error is logged and shown on the GDM login screen.

    :return: True if the hostname is valid, False otherwise
    :rtype: bool
    """
    if hostnameIsValid():
        _setLoginScreenWarning(None)
        return True

    message = f"The hostname '{hostname()}' is longer than {constants.maxHostnameLength} characters, domain logins will not work! Please use a shorter hostname in the devices.csv."
    logging.error(message)
    _setLoginScreenWarning(message)
    return False

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
    return ldapHelper.searchOne(f"(sAMAccountName={ldapHelper.escape(hostname())}$)")

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

# --------------------
# - Helper functions -
# --------------------

def _setLoginScreenWarning(message):
    """
    Show a warning on the GDM login screen or remove it

    :param message: The message to show, None to remove the warning
    :type message: str
    :return: True if the warning was changed, False otherwise
    :rtype: bool
    """
    if not os.path.isdir(constants.gdmDconfDir):
        return False

    if message == None:
        if not os.path.exists(constants.loginScreenWarningFile):
            return False
        os.remove(constants.loginScreenWarningFile)
    else:
        content = f"[org/gnome/login-screen]\nbanner-message-enable=true\nbanner-message-text=\"{message}\"\n"
        if os.path.exists(constants.loginScreenWarningFile):
            with open(constants.loginScreenWarningFile, "r") as file:
                if file.read() == content:
                    return False
        with open(constants.loginScreenWarningFile, "w") as file:
            file.write(content)

    subprocess.call(["/usr/share/gdm/generate-config"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not _userIsLoggedIn():
        subprocess.call(["systemctl", "try-restart", "gdm"])
    return True

def _userIsLoggedIn():
    """
    Check if a user (other than the display manager) is logged in

    :return: True or False
    :rtype: bool
    """
    result = subprocess.run(["loginctl", "list-users", "--no-legend"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for line in result.stdout.split("\n"):
        columns = line.split()
        if len(columns) >= 2 and not columns[1].startswith("gdm"):
            return True
    return False
