import os, sys, subprocess, configparser
from linuxmusterLinuxclient7 import logging, computer

def join(domain, user):
    """
    Joins the computer to an AD

    :param domain: The domain to join
    :type domain: str
    :param user: The admin user used for joining
    :type user: str
    :return: True on success, False otherwise
    :rtype: bool
    """
    # join the domain using the kerberos ticket
    joinCommand = ["realm", "join", "-v", domain, "-U", user]
    if subprocess.call(joinCommand) != 0:
        print()
        logging.error('Failed! Did you enter the correct password?')
        return False

    logging.info("It looks like the domain was joined successfully.")
    return True

def leave(domain):
    """
    Leave a domain

    :param domain: The domain to leave
    :type domain: str
    :return: True on success, False otherwise
    :rtype: bool
    """
    leaveCommand = ["realm", "leave", domain]
    return subprocess.call(leaveCommand) == 0

def leaveAll():
    """
    Leaves all joined domains

    :return: True on success, False otherwise
    :rtype: bool
    """
    logging.info("Cleaning / leaving all domain joins")

    rc, joinedDomains = getJoinedDomains()
    if not rc:
        return False

    for joinedDomain in joinedDomains:
        logging.info("* {}".format(joinedDomain))
        if not leave(joinedDomain):
            logging.error("-> Failed! Aborting!")
            return False
    
    logging.info("-> Done!")
    return True

def isJoined():
    """
    Checks if the computer is joined to a domain

    :return: True if it is joined to one or more domains, False otherwise
    :rtype: bool
    """
    rc, joinedDomains = getJoinedDomains()
    if not rc:
        return False
    else:
        return len(joinedDomains) > 0

def pullKerberosTicketForComputerAccount():
    """
    Pulls a kerberos ticket using the computer account from `/etc/krb5.keytab`

    :return: True on success, False otherwise
    :rtype: bool
    """
    return subprocess.call(["kinit", "-k", computer.krbHostName()]) == 0

def verifyDomainJoin():
    """
    Checks if the domain join actually works.

    :return: True if it does, False otherwise
    :rtype: bool
    """
    logging.info("Testing if the domain join actually works")
    if not isJoined():
        logging.error("No domain is joined!")
        return False
    
    logging.info("* Checking if the group \"domain users\" exists")
    if subprocess.call(["getent", "group", "domain users"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
        logging.error("The \"domain users\" group does not exists! Users wont be able to log in!")
        logging.error("This is sometimes related to /etc/nsswitch.conf.")
        return False

    # Try to get a kerberos ticket for the computer account
    logging.info("* Trying to get a kerberos ticket for the Computer Account")
    if not pullKerberosTicketForComputerAccount():
        logging.error("Could not get a kerberos ticket for the Computer Account!")
        logging.error("Logins of non-cached users WILL NOT WORK!")
        logging.error("Please try to re-join the Domain.")
        return False
    
    
    logging.info("The domain join is working!")
    return True

def getJoinedDomains():
    """
    Returns all joined domains

    :return: Tuple (success, list of joined domians)
    :rtype: tuple
    """
    result = subprocess.run("realm list --name-only", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

    if result.returncode != 0:
        logging.error("Failed to read domain joins!")
        return False, None

    return True, list(filter(None, result.stdout.split("\n")))

def discoverDomains(domain=None):
    """
    Searches for avialable domains on the current network

    :param domain: The domain to discover (optional)
    :type domain: str
    :return: Tuple (success, list of available domains)
    :rtype: tuple
    """
    command = ["realm", "discover", "--name-only"]
    if domain != None:
        command.append(domain)
        
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    if result.returncode != 0:
        logging.error("Failed to discover available domains!")
        return False, None

    return True, list(filter(None, result.stdout.split("\n")))

def getDomainConfig(domain):
    """
    Looks up all relevant properties of a domain:
    - domain controller IP
    - domain name

    :param domain: The domain to check
    :type domain: str
    :return: Tuple (success, dict with domain config)
    :rtype: tuple
    """
    result = subprocess.run("adcli info '{}'".format(domain), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

    if result.returncode != 0:
        logging.error("Failed to get details of domain {}!".format(domain))
        return False, None

    rawConfig = _readConfigFromString(result.stdout)
    try:
        rawDomainConfig = rawConfig["domain"]
    except KeyError:
        logging.error("Error when reading domain details")
        return False, None

    domainConfig = {}

    try:
        domainConfig["domain-controller"] = rawDomainConfig["domain-controller"]
        domainConfig["domain-name"] = rawDomainConfig["domain-name"]
    except KeyError:
        logging.error("Error when reading domain details (2)")
        return False, None

    return True, domainConfig

def clearUserCache():
    """
    Clears the local user cache

    :return: True on success, False otherwise
    :rtype: bool
    """
    # clean sssd cache
    logging.info("Cleaning sssd cache.")
    subprocess.call(["sssctl", "cache-remove", "--stop", "--start", "--override"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return True

# --------------------
# - Helper functions -
# --------------------

def _readConfigFromString(string):
    configParser = configparser.ConfigParser()
    configParser.read_string(string)
    return configParser