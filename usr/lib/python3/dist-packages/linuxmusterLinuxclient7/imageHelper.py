import os, subprocess, shutil
from linuxmusterLinuxclient7 import logging, setup, realm, user, constants, printers, fileHelper

def prepareForImage(unattended=False):
    logging.info("#### Image preparation ####")

    try:
        if not _testDomainJoin(unattended):
            return False

        if not _upgradeSystem(unattended):
            return False

        if not _clearCaches(unattended):
            return False

        if not _clearUserHomes(unattended):
            return False

        if not _clearUserCache(unattended):
            return False

        if not _clearPrinters(unattended):
            return False

        if not _clearLogs(unattended):
            return False

        if not _emptyTrash(unattended):
            return False

    except KeyboardInterrupt:
        print()
        logging.info("Cancelled.")
        return False

    print()
    logging.info("####    Image preparation done      ####")
    logging.info("#### You may create an Image now :) ####")
    print()
    return True

# --------------------
# - Helper functions -
# --------------------

def _askStep(step, printPlaceholder=True):
    if printPlaceholder:
        print()
    response = input("Do you want to {}? (y/n): ".format(step))
    result = response in ["y", "Y", "j", "J"]
    if result:
        print()
    return result

def _testDomainJoin(unattended=False):
    if not unattended and not _askStep("test if the domain join works"):
        return True

    return setup.status()

def _upgradeSystem(unattended=False):
    if not unattended and not _askStep("update this computer now"):
        return True
    
    # Perform an update
    logging.info("Updating this computer now...")

    if subprocess.call(["apt", "update"]) != 0:
        logging.error("apt update failed!")
        return False
    
    if subprocess.call(["apt", "dist-upgrade", "-y"]) != 0:
        logging.error("apt dist-upgrade failed!")
        return False
    
    if subprocess.call(["apt", "autoremove", "-y"]) != 0:
        logging.error("apt autoremove failed!")
        return False
    
    if subprocess.call(["apt", "clean", "-y"]) != 0:
        logging.error("apt clean failed!")
        return False

    return True
    
def _clearCaches(unattended=False):    
    if not unattended and not _askStep("clear journalctl and apt caches now"):
        return True

    logging.info("Cleaning caches..")
    logging.info("* apt")
    fileHelper.deleteAllInDirectory("/var/lib/apt/lists/")
    logging.info("* journalctl")
    subprocess.call(["journalctl", "--flush", "--rotate"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call(["journalctl", "--vacuum-time=1s"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info("Done.")
    return True

def _checkLoggedInUsers():
    result = subprocess.run("who -s | awk '{ print $1 }'", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

    if result.returncode != 0:
        logging.error("Failed to get logged in users!")
        return False, None

    loggedInUsers = list(filter(None, result.stdout.split("\n")))

    for loggedInUser in loggedInUsers:
        if user.isUserInAD(loggedInUser):
            logging.error("User {} is still logged in, please log out first! Aborting!".format(loggedInUser))
            return False

    return True

def _clearUserCache(unattended=False):
    if not unattended and not _askStep("clear all cached users now"):
        return True

    if not _checkLoggedInUsers():
        return False

    realm.clearUserCache()

    logging.info("Done.")

    return realm.clearUserCache()

def _unmountAllCifsMounts():
    logging.info("Unmounting all CIFS mounts!")
    if subprocess.call(["umount",  "-a", "-t", "cifs", "-l"]) != 0:
        logging.info("Failed!")
        return False

    # double check (just to be sure)
    result = subprocess.run("mount", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)

    if result.returncode != 0:
        logging.error("Failed to get mounts!")
        return False

    if ("cifs" in result.stdout) or ("CIFS" in result.stdout):
        logging.error("There are still shares mounted!")
        logging.info("Use \"mount | grep cifs\" to view them.")
        return False

    return True

def _clearUserHomes(unattended=False):
    print("\nCAUTION! This will delete all userhomes of AD users!")
    if not unattended and not _askStep("clear all user homes now", False):
        return True

    if not _checkLoggedInUsers():
        return False

    if not _unmountAllCifsMounts():
        logging.info("Aborting deletion of user homes to prevent deleting data on the server.")
        return False

    userHomes = os.listdir("/home")

    logging.info("Deleting all user homes now!")
    for userHome in userHomes:
        if not user.isUserInAD(userHome):
            logging.info("* {} [SKIPPED]".format(userHome))
            continue

        logging.info("* {}".format(userHome))
        try:
            shutil.rmtree("/home/{}".format(userHome))
        except Exception as e:
            logging.error("* FAILED!")
            logging.exception(e)
        
        try:
            shutil.rmtree(constants.hiddenShareMountBasepath.format(userHome))
        except:
            pass
    
    logging.info("Done.")
    return True

def _clearPrinters(unattended=False):
    print("\nCAUTION! This will delete all printers of {}!".format(constants.templateUser))
    print("This makes sure that local printers do not conflict with remote printers defined by GPOs.")
    if not unattended and not _askStep("remove all local printers of {}".format(constants.templateUser), False):
        return True
    
    if not printers.uninstallAllPrintersOfUser(constants.templateUser):
        return False

    return True

def _clearLogs(unattended=False):
    if not unattended and not _askStep("clear the syslog"):
        return True
    
    if not fileHelper.deleteFile("/var/log/syslog"):
        return False

    subprocess.call(["sudo", "service", "rsyslog", "restart"])

    return True

def _emptyTrash(unattended=False):
    if not unattended and not _askStep("clear the Trash of linuxadmin"):
        return True

    if not fileHelper.deleteAllInDirectory("/home/{}/.local/share/Trash".format(constants.templateUser)):
        return False
    
    return True