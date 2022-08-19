#
# This is used to run hooks
#

from enum import Enum
import os, subprocess
from linuxmusterLinuxclient7 import logging, constants, user, config, computer, environment, setup, shares

class Type(Enum):
    """
    Enum containing all hook types
    """

    Boot = 0
    """The onBoot hook
    """
    Shutdown = 1
    """The on Shutdown hook
    """
    LoginAsRoot = 2
    """The onLoginAsRoot hook
    """
    Login = 3
    """The onLogin hook
    """
    SessionStarted = 4
    """The onSession started hook
    """
    LogoutAsRoot = 5
    LoginLogoutAsRoot = 6

remoteScriptNames = {
    Type.Boot: "sysstart.sh",
    Type.Login: "logon.sh",
    Type.SessionStarted: "sessionstart.sh",
    Type.Shutdown: "sysstop.sh"
}

_remoteScriptInUserContext = {
    Type.Boot: False,
    Type.Login: True,
    Type.SessionStarted: True,
    Type.Shutdown: False
}

def runLocalHook(hookType):
    """
    Run all scripts in a local hookdir

    :param hookType: The type of hook to run
    :type hookType: hooks.Type
    """    
    hookDir = _getLocalHookDir(hookType)
    logging.info("=== Running local hook on{0} in {1} ===".format(hookType.name, hookDir))
    if os.path.exists(hookDir):
        _prepareEnvironment()
        for fileName in sorted(os.listdir(hookDir)):
            filePath = hookDir + "/" + fileName
            _runHookScript(filePath)
    logging.info("===> Finished running local hook on{0} ===".format(hookType.name))


def runRemoteHook(hookType):
    """
    Run hookscript from sysvol

    :param hookType: The type of hook to run
    :type hookType: hooks.Type
    """    
    logging.info("=== Running remote hook on{0} ===".format(hookType.name))
    rc, hookScripts = _getRemoteHookScripts(hookType)

    if rc:
        _prepareEnvironment()
        _runHookScript(hookScripts[0])
        _runHookScript(hookScripts[1])

    logging.info("===> Finished running remote hook on{0} ===".format(hookType.name))

def runHook(hookType):
    """
    Executes hooks.runLocalHook() and hooks.runRemoteHook()

    :param hookType: The type of hook to run
    :type hookType: hooks.Type
    """    
    runLocalHook(hookType)
    runRemoteHook(hookType)

def getLocalHookScript(hookType):
    """Get the path of a local hookscript

    :param hookType: The type of hook script to get the path for
    :type hookType: hooks.Type
    :return: The path
    :rtype: str
    """
    return "{0}/on{1}".format(constants.scriptDir,hookType.name)

def shouldHooksBeExecuted(overrideUsername=None):
    """Check if hooks should be executed

    :param overrideUsername: Override the username to check, defaults to None
    :type overrideUsername: str, optional
    :return: True if hooks should be executed, fale otherwise
    :rtype: bool
    """
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

def _prepareEnvironment():
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

def _getLocalHookDir(hookType):
    return "{0}/on{1}.d".format(constants.etcBaseDir,hookType.name)

def _getRemoteHookScripts(hookType):
    if not hookType in remoteScriptNames:
        return False, None

    rc, networkConfig = config.network()

    if not rc:
        logging.error("Could not execute server hooks because the network config could not be read")
        return False, None

    if _remoteScriptInUserContext[hookType]:
        rc, attributes = user.readAttributes()
        if not rc:
            logging.error("Could not execute server hooks because the user config could not be read")
            return False, None
    else:
        rc, attributes = computer.readAttributes()
        if not rc:
            logging.error("Could not execute server hooks because the computer config could not be read")
            return False, None

    try:
        domain = networkConfig["domain"]
        school = attributes["sophomorixSchoolname"]
        scriptName = remoteScriptNames[hookType]
    except:
        logging.error("Could not execute server hooks because the computer/user config is missing attributes")
        return False, None

    rc, sysvolPath = shares.getLocalSysvolPath()
    if not rc:
        logging.error("Could not execute server hook {} because the sysvol could not be mounted!\n")
        return False, None

    hookScriptPathTemplate = "{0}/{1}/scripts/{2}/{3}/linux/{4}".format(sysvolPath, domain, school, "{}", scriptName)

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

    result = subprocess.call([filePath])

    logging.info("==> Script {0} finished with exit code {1} ==".format(filePath, result))

def _writeEnvironment(environment):
    for key in environment:
        os.putenv(key, environment[key])
