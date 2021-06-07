import os, codecs, sys, shutil, subprocess
from pathlib import Path
from linuxmusterLinuxclient7 import logging, constants, hooks, config


def applyAll():
    logging.info('Applying all configuration templates:')

    templateDir = constants.configFileTemplateDir
    for templateFile in os.listdir(templateDir):
        templatePath = templateDir + '/' + templateFile
        logging.info('* ' + templateFile + ' ...')
        if not _apply(templatePath):
            logging.error("Aborting!")
            return False

    # reload sctemctl
    logging.info('Reloading systemctl ... ')
    if not subprocess.call(["systemctl", "daemon-reload"]) == 0:
        logging.error("Failed!")
        return False

    return True

# --------------------
# - Helper functions -
# --------------------


def _apply(templatePath):
    try:
        # read template file
        rc, fileData = _readTextfile(templatePath)

        if not rc:
            logging.error('Failed!')
            return False

        fileData = _resolveVariables(fileData)

        # get target path
        firstLine = fileData.split('\n')[0]
        targetFilePath = firstLine.partition(' ')[2]

        # remove first line (the target file path)
        fileData = fileData[fileData.find('\n'):]

        # never ever overwrite sssd.conf, this will lead to issues!
        # sssd.conf is written by `realm join`!
        if targetFilePath in constants.notTemplatableFiles:
            logging.warning("Skipping forbidden file {}".format(targetFilePath))
            return True

        # create target directory
        Path(Path(targetFilePath).parent.absolute()).mkdir(parents=True, exist_ok=True)

        # remove comment lines beginning with # from .xml files
        if targetFilePath.endswith('.xml'):
            fileData = _stripComment(fileData)

        # write config file
        logging.debug("-> to {}".format(targetFilePath))
        with open(targetFilePath, 'w') as targetFile:
            targetFile.write(fileData)

        return True

    except Exception as e:
        logging.error('Failed!')
        logging.exception(e)
        return False

def _resolveVariables(fileData):
    # replace placeholders with values
    rc, networkConfig = config.network()

    if not rc:
        return False, None

    # network
    fileData = fileData.replace('@@serverHostname@@', networkConfig["serverHostname"])
    fileData = fileData.replace('@@domain@@', networkConfig["domain"])
    fileData = fileData.replace('@@realm@@', networkConfig["realm"])

    # constants
    fileData = fileData.replace('@@userTemplateDir@@', constants.userTemplateDir)
    fileData = fileData.replace('@@hiddenShareMountBasepath@@', constants.hiddenShareMountBasepath.format("%(USER)"))

    # hooks
    fileData = fileData.replace('@@hookScriptBoot@@', hooks.getLocalHookScript(hooks.Type.Boot))
    fileData = fileData.replace('@@hookScriptShutdown@@', hooks.getLocalHookScript(hooks.Type.Shutdown))
    fileData = fileData.replace('@@hookScriptLoginLogoutAsRoot@@', hooks.getLocalHookScript(hooks.Type.LoginLogoutAsRoot))
    fileData = fileData.replace('@@hookScriptSessionStarted@@', hooks.getLocalHookScript(hooks.Type.SessionStarted))

    return fileData

# read textfile in variable
def _readTextfile(filePath):
    if not os.path.isfile(filePath):
        return False, None
    try:
        infile = codecs.open(filePath ,'r', encoding='utf-8', errors='ignore')
        content = infile.read()
        infile.close()
        return True, content
    except Exception as e:
        logging.info('Cannot read ' + filePath + '!')
        logging.exception(e)
        return False, None

# remove lines beginning with #
def _stripComment(fileData):
    filedata_stripped = ''
    for line in fileData.split('\n'):
        if line[:1] == '#':
            continue
        else:
            if filedata_stripped == '':
                filedata_stripped = line
            else:
                filedata_stripped = filedata_stripped + '\n' + line
    return filedata_stripped