import os
from linuxmusterLinuxclient7 import constants, user, logging

def export(keyValuePair):
    logging.debug("Saving export '{}' to tmp file".format(keyValuePair))
    
    envList = keyValuePair.split("=")
    if len(envList) == 2:
        os.putenv(envList[0], envList[1])
    
    return _appendToTmpEnvFile("export", keyValuePair)

def unset(keyValuePair):
    logging.debug("Saving unset '{}' to tmp file".format(keyValuePair))
    return _appendToTmpEnvFile("unset", keyValuePair)

# --------------------
# - Helper functions -
# --------------------

def _isApplicable():
    if not user.isInAD():
        logging.error("Modifying environment variables of non-AD users is not supported by lmn-export and lmn-unset!")
        return False
    elif "LinuxmusterLinuxclient7EnvFixActive" not in os.environ or os.environ["LinuxmusterLinuxclient7EnvFixActive"] != "1":
        logging.error("lmn-export and lmn-unset may only be used inside of linuxmuster-linuxclient7 hooks!")
        return False
    else:
        return True

def _appendToTmpEnvFile(mode, keyValuePair):
    if not _isApplicable():
        return False
    
    tmpEnvironmentFilePath = constants.tmpEnvironmentFilePath.format(user.username())
    fileOpenMode = "a" if os.path.exists(tmpEnvironmentFilePath) else "w"

    try:
        with open(tmpEnvironmentFilePath, fileOpenMode) as tmpEnvironmentFile:
            tmpEnvironmentFile.write("\n{0} '{1}'".format(mode, keyValuePair))
            return True
    except Exception as e:
        logging.exception(e)
        return False