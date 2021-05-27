import os, pwd, sys, shutil, re
from linuxmusterLinuxclient7 import logging, constants, user, config, computer
from pathlib import Path

def mountShare(networkPath, shareName = None, hiddenShare = False, username = None):
    networkPath = networkPath.replace("\\", "/")
    username = _getDefaultUsername(username)

    if user.isRoot():
        return _mountShare(username, networkPath, shareName, hiddenShare, True)
    else:
        mountpoint = _getShareMountpoint(networkPath, username, hiddenShare, shareName)
        # This will call _mountShare() directly with root privileges
        return _mountShareWithoutRoot(networkPath, shareName, hiddenShare), mountpoint

def getMountpointOfRemotePath(remoteFilePath, hiddenShare = False, username = None, autoMount = True):
    remoteFilePath = remoteFilePath.replace("\\", "/")
    username = _getDefaultUsername(username)

    # get basepath fo remote file path
    # this turns //server/sysvol/linuxmuster.lan/Policies into //server/sysvol
    pattern = re.compile("(^\\/\\/[^\\/]+\\/[^\\/]+)")
    match = pattern.search(remoteFilePath)

    if match == None:
        logging.error("Cannot get local file path of {} beacuse it is not a valid path!".format(remoteFilePath))
        return False, None

    shareBasepath = match.group(0)

    if autoMount:
       rc, mointpoint = mountShare(shareBasepath, hiddenShare=hiddenShare, username=username)
       if not rc:
           return False, None
    
    # calculate local path
    shareMountpoint = _getShareMountpoint(shareBasepath, username, hiddenShare, shareName=None)
    localFilePath = remoteFilePath.replace(shareBasepath, shareMountpoint)

    return True, localFilePath

def unmountAllSharesOfUser(username):
    logging.info("=== Trying to unmount all shares of user {0} ===".format(username))
    for basedir in [constants.shareMountBasepath, constants.hiddenShareMountBasepath]:
        shareMountBasedir = basedir.format(username)

        try:
            mountedShares = os.listdir(shareMountBasedir)
        except FileNotFoundError:
            logging.info("Mount basedir {} does not exist -> nothing to unmount".format(shareMountBasedir))
            continue

        for share in mountedShares:
            _unmountShare("{0}/{1}".format(shareMountBasedir, share))
    
        if len(os.listdir(shareMountBasedir)) > 0:
            logging.warning("* Mount basedir {} is not empty so not removed!".format(shareMountBasedir))
            return
        else:
            # Delete the directory
            logging.info("Deleting {0}...".format(shareMountBasedir))
            try:
                shutil.rmtree(shareMountBasedir)
            except Exception as e:
                logging.error("FAILED!")
                logging.exception(e)

    logging.info("===> Finished unmounting all shares of user {0} ===".format(username))

def getLocalSysvolPath():
    rc, networkConfig = config.network()
    if not rc:
        return False, None

    networkPath = "//{}/sysvol".format(networkConfig["serverHostname"])
    return getMountpointOfRemotePath(networkPath, True)

# --------------------
# - Helper functions -
# --------------------

# useCruidOfExecutingUser:
#  defines if the ticket cache of the user executing the mount command should be used.
#  If set to False, the cache of the user with the given username will be used.
#  This parameter influences the `cruid` mount option.
def _mountShare(username, networkPath, shareName, hiddenShare, useCruidOfExecutingUser=False):

    mountpoint = _getShareMountpoint(networkPath, username, hiddenShare, shareName)

    mountCommandOptions = "file_mode=0700,dir_mode=0700,sec=krb5,nodev,nosuid,mfsymlinks,nobrl,vers=3.0,user={}".format(username)
    rc, networkConfig = config.network()
    domain = None

    if rc:
        domain = networkConfig["domain"]
        mountCommandOptions += ",domain={}".format(domain.upper())

    try:
        pwdInfo = pwd.getpwnam(username)
        uid = pwdInfo.pw_uid
        gid = pwdInfo.pw_gid
        mountCommandOptions += ",gid={0},uid={1}".format(gid, uid)

        if not useCruidOfExecutingUser:
            mountCommandOptions += ",cruid={0}".format(uid)

    except KeyError:
        uid = -1
        gid = -1
        logging.warning("Uid could not be found! Continuing anyway!")

    mountCommand = ("mount.cifs "
        "-o {0} "
        "'{1}' '{2}' 2>/dev/null".format(mountCommandOptions, networkPath, mountpoint))

    logging.debug("Trying to mount {0} to {1}".format(networkPath, mountpoint))
    logging.debug("* Creating directory...")

    try:
        Path(mountpoint).mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        # Test if a share is already mounted there
        if _directoryIsMountpoint(mountpoint):
            logging.debug("* The mountpoint is already mounted.")
            return True, mountpoint
        else:
            logging.warning("* The target directory already exists, proceeding anyway!")

    logging.debug("* Executing {} ".format(mountCommand))
    logging.debug("* Trying to mount...")
    if not os.system(mountCommand) == 0:
        logging.fatal("* Error mounting share {0} to {1}!\n".format(networkPath, mountpoint))
        return False, mountpoint

    logging.debug("* Success!")

    # hide the shares parent dir (/home/%user/media) in case it is not a hidden share
    if not hiddenShare:
        try:
            hiddenFilePath = "{}/../../.hidden".format(mountpoint)
            logging.debug("* hiding parent dir {}".format(hiddenFilePath))
            hiddenFile = open(hiddenFilePath, "w+")
            hiddenFile.write(mountpoint.split("/")[-2])
            hiddenFile.close()
        except:
            logging.warning("Could not hide parent dir of share {}".format(mountpoint))

    return True, mountpoint

def _unmountShare(mountpoint):
    # check if mountpoint exists
    if (not os.path.exists(mountpoint)) or (not os.path.isdir(mountpoint)):
        logging.warning("* Could not unmount {}, it does not exist.".format(mountpoint))

    # Try to unmount share
    logging.info("* Trying to unmount {0}...".format(mountpoint))
    if not os.system("umount '{0}'".format(mountpoint)) == 0:
        logging.warning("* Failed!")
        if _directoryIsMountpoint(mountpoint):
            logging.warning("* It is still mounted! Exiting!")
            # Do not delete in this case! We might delete userdata!
            return
        logging.info("* It is not mounted! Continuing!")

    # check if the mountpoint is empty
    if len(os.listdir(mountpoint)) > 0:
        logging.warning("* mountpoint {} is not empty so not removed!".format(mountpoint))
        return

    # Delete the directory
    logging.info("* Deleting {0}...".format(mountpoint))
    try:
        shutil.rmtree(mountpoint)
    except Exception as e:
        logging.error("* FAILED!")
        logging.exception(e)

def _getDefaultUsername(username=None):
    if username == None:
        if user.isRoot():
            username = computer.hostname().upper() + "$"
        else:
            username = user.username()
    return username

def _mountShareWithoutRoot(networkPath, name, hidden):
    if hidden:
        hidden = "--hidden"
    else:
        hidden = ""

    return os.system("sudo /usr/share/linuxmuster-linuxclient7/scripts/sudoTools mount-share --path '{0}' --name '{1}' {2}".format(networkPath, name, hidden)) == 0

def _getShareMountpoint(networkPath, username, hidden, shareName = None):
    logging.debug("Calculating mountpoint of {}".format(networkPath))

    if shareName == None or shareName == "None":
        shareName = networkPath.split("/")[-1]

    if hidden:
        return "{0}/{1}".format(constants.hiddenShareMountBasepath.format(username), shareName)
    else:
        return "{0}/{1}".format(constants.shareMountBasepath.format(username), shareName)

def _directoryIsMountpoint(dir):
    return os.system("mountpoint -q '{}'".format(dir)) == 0
