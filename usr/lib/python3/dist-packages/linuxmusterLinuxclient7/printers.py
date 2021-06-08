import os, subprocess, re
from linuxmusterLinuxclient7 import logging, user

def installPrinter(networkPath, name=None, username=None):
    if username == None:
        username = user.username()

    if user.isRoot():
        return _installPrinter(username, networkPath, name)
    else:
        # This will call installPrinter() again with root privileges
        return _installPrinterWithoutRoot(networkPath, name)

    pass

def uninstallAllPrintersOfUser(username):
    logging.info("Uninstalling all printers of {}".format(username))
    rc, installedPrinters = _getInstalledPrintersOfUser(username)

    if not rc:
        logging.error("Error getting printers!")
        return False

    for installedPrinter in installedPrinters:
        if not _uninstallPrinter(installedPrinter):
            return False

    return True

def translateSambaToIpp(networkPath):
    networkPath = networkPath.replace("\\", "/")
    # path has to be translated: \\server\EW-FARBLASER -> ipp://server/printers/EW-farblaser
    pattern = re.compile("\\/\\/([^/]+)\\/(.*)")

    result = pattern.findall(networkPath)
    if len(result) != 1 or len(result[0]) != 2:
        logging.error("Cannot convert printer network path from samba to ipp, as it is invalid: {}".format(networkPath))
        return False, None

    ippNetworkPath = "ipp://{0}/printers/{1}".format(result[0][0], result[0][1])
    return True, ippNetworkPath

# --------------------
# - Helper functions -
# --------------------

def _installPrinter(username, networkPath, name):
    logging.debug("Installing Printer {0} on {1}".format(name, networkPath))
    installCommand = ["lpadmin", "-p", name, "-E", "-v", networkPath, "-m", "everywhere", "-u", f"allow:{username}"]
    logging.debug("* running '{}'".format(" ".join(installCommand)))

    if not subprocess.call(installCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
        logging.fatal(f"* Error installing printer {name} on {networkPath}!\n")
        return False

    logging.debug("* Success!")
    return True

def _installPrinterWithoutRoot(networkPath, name):
    return subprocess.call(["sudo", "/usr/share/linuxmuster-linuxclient7/scripts/sudoTools", "install-printer", "--path", networkPath, "--name", name]) == 0

def _getInstalledPrintersOfUser(username):
    logging.info(f"Getting installed printers of {username}")
    command = f"lpstat -U {username} -p"
    #logging.debug("running '{}'".format(command))

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

    if not result.returncode == 0:
        logging.info("No Printers installed.")
        return True, []

    rawInstalledPrinters = list(filter(None, result.stdout.split("\n")))
    installedPrinters = []
    
    for rawInstalledPrinter in rawInstalledPrinters:
        rawInstalledPrinterList = list(filter(None, rawInstalledPrinter.split(" ")))
        
        if len(rawInstalledPrinterList) < 2:
            continue

        installedPrinter = rawInstalledPrinterList[1]
        installedPrinters.append(installedPrinter)

    return True, installedPrinters

def _uninstallPrinter(name):
    logging.info("* Uninstalling Printer {}".format(name))
    uninstallCommand = ["lpadmin", "-x", name]
    #logging.debug("* running '{}'".format(installCommand))

    if not subprocess.call(uninstallCommand) == 0:
        logging.error("* Error uninstalling printer!")
        return False

    return True
