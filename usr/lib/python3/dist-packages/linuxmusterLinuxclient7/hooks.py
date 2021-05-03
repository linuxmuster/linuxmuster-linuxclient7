#
# This is used to run hooks
#

from enum import Enum
import os, subprocess
from linuxmusterLinuxclient7 import logging, constants, user, config, computer, environment, setup

class Type(Enum):
    Boot = 0
    Shutdown = 1
    LoginAsRoot = 2
    Login = 3
    SessionStarted = 4
    LogoutAsRoot = 5
    LoginLogoutAsRoot = 6

remoteScriptNames = {
    Type.Boot: "sysstart.sh", # not used currently
    Type.Login: "logon.sh",
    Type.SessionStarted: "sessionstart.sh",
    Type.Shutdown: "sysstop.sh" # not used currently
}

def runLocalHook(hookType):
    logging.info("=== Running local hook on{0} ===".format(hookType.name))
    hookDir = _getLocalHookDir(hookType)
    if os.path.exists(hookDir):
        for fileName in os.listdir(hookDir):
            filePath = hookDir + "/" + fileName
            _runHookScript(filePath)
    logging.info("===> Finished running local hook on{0} ===".format(hookType.name))


def runRemoteHook(hookType):
    logging.info("=== Running remote hook on{0} ===".format(hookType.name))
    rc, hookScripts = _getRemoteHookScripts(hookType)

    if rc:
        _runHookScript(hookScripts[0])
        _runHookScript(hookScripts[1])

    logging.info("===> Finished running remote hook on{0} ===".format(hookType.name))

def runHook(hookType):
    runLocalHook(hookType)
    runRemoteHook(hookType)

def getLocalHookScript(hookType):
    return "{0}/on{1}".format(constants.scriptDir,hookType.name)

def createSessionAutostartFile():
    pass

def shouldHooksBeExecuted(overrideUsername=None):
    # check if linuxmuster-linuxclient7 is setup
    if not setup.isSetup():
        logging.info("==== Linuxmuster-linuxclient7 is not setup, exiting ====")
        return False

    # check if the computer is joined
    if not computer.isInAD():
        logging.info("==== This Client is not joined to any domain, exiting ====")
        return False

    # Check if the user is an AD user
    if overrideUsername == None:
        overrideUsername = user.username()

    if not user.isUserInAD(overrideUsername):
        logging.info("==== {0} is not an AD user, exiting ====".format(user.username()))
        return False
    
    return True

# --------------------
# - Helper functions -
# --------------------

def _getLocalHookDir(hookType):
    return "{0}/on{1}.d".format(constants.etcBaseDir,hookType.name)

def _getRemoteHookScripts(hookType):
    if not hookType in remoteScriptNames:
        return False, None

    rc, networkConfig = config.network()

    if not rc:
        logging.error("Could not execute server hooks because the network config could not be read")
        return False, None

    rc, userAttributes = user.readAttributes()
    if not rc:
        logging.error("Could not execute server hooks because the user config could not be read")
        return False, None

    try:
        domain = networkConfig["domain"]
        school = userAttributes["sophomorixSchoolname"]
        username = userAttributes["sAMAccountName"]
        scriptName = remoteScriptNames[hookType]
    except:
        logging.error("Could not execute server hooks because the user config is missing attributes")
        return False, None

    hookScriptPathTemplate = "/srv/samba/{0}/sysvol/{1}/scripts/{2}/{3}/linux/{4}".format(username, domain, school, "{}", scriptName)

    return True, [hookScriptPathTemplate.format("lmn"), hookScriptPathTemplate.format("custom")]

# parameter must be a dict of {"prefix": dict}
def _dictsToEnv(dictsAndPrefixes):
    environmentDict = {}
    for prefix in dictsAndPrefixes:
        for key in dictsAndPrefixes[prefix]:
            if type(dictsAndPrefixes[prefix][key]) is list:
                environmentDict[prefix + "_" + key] = "\n".join(dictsAndPrefixes[prefix][key])
            else:
                environmentDict[prefix + "_" + key] = dictsAndPrefixes[prefix][key]

    return environmentDict

def _runHookScript(filePath):
    if not os.path.isfile(filePath):
        logging.warning("* File {0} should be executed as hook but does not exist!".format(filePath))
        return
    if not os.access(filePath, os.X_OK):
        logging.warning("* File {0} is in hook dir but not executable!".format(filePath))
        return

    logging.info("== Executing script {0} ==".format(filePath))

    dictsAndPrefixes = {}

    rc, networkConfig = config.network()
    if rc:
        dictsAndPrefixes["Network"] = networkConfig

    rc, userConfig = user.readAttributes()
    if rc:
        dictsAndPrefixes["User"] = userConfig

    rc, computerConfig = computer.readAttributes()
    if rc:
        dictsAndPrefixes["Computer"] = computerConfig

    environment = _dictsToEnv(dictsAndPrefixes)
    _writeEnvironment(environment)

    result = os.system(filePath)

    logging.info("==> Script {0} finished with exit code {1} ==".format(filePath, result))

def _writeEnvironment(environment):
    for key in environment:
        os.putenv(key, environment[key])