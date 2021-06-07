import os, sys, subprocess, configparser
from linuxmusterLinuxclient7 import logging, computer

def join(domain, user):
    # join the domain using the kerberos ticket
    joinCommand = f"realm join -v {domain} -U {user}"
    if os.system(joinCommand) != 0:
        print()
        logging.error('Failed! Did you enter the correct password?')
        return False

    logging.info("It looks like the domain was joined successfully.")
    return True

def leave(domain):
    return os.system("realm leave {}".format(domain)) == 0

def leaveAll():
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
    rc, joinedDomains = getJoinedDomains()
    if not rc:
        return False
    else:
        return len(joinedDomains) > 0

def pullKerberosTicketForComputerAccount():
    return os.system("kinit -k {}$".format(computer.hostname().upper())) == 0

def verifyDomainJoin():
    logging.info("Testing if the domain join actually works")
    if not isJoined():
        logging.error("No domain is joined!")
        return False
    
    logging.info("* Checking if the group \"domain users\" exists")
    if os.system("getent group \"domain users\" > /dev/null") != 0:
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
    result = subprocess.run("realm list --name-only", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

    if result.returncode != 0:
        logging.error("Failed to read domain joins!")
        return False, None

    return True, list(filter(None, result.stdout.split("\n")))

def discoverDomains():
    result = subprocess.run("realm discover --name-only", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

    if result.returncode != 0:
        logging.error("Failed to discover available domains!")
        return False, None

    return True, list(filter(None, result.stdout.split("\n")))

def getDomainConfig(domain):
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
    # clean sssd cache
    logging.info("Cleaning sssd cache.")
    os.system("sssctl cache-remove --stop --start --override 2> /dev/null")
    return True

# --------------------
# - Helper functions -
# --------------------

def _readConfigFromString(string):
    configParser = configparser.ConfigParser()
    configParser.read_string(string)
    return configParser