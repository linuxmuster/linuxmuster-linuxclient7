import os, pwd, sys, shutil, re
from linuxmusterLinuxclient7 import logging, constants, user
from pathlib import Path

def mountShare(networkPath, shareName = None, hiddenShare = False, username = None):
    networkPath = networkPath.replace("\\", "/")
    if username == None:
        username = user.username()

    mountpoint = _getShareMountpoint(networkPath, username, hiddenShare, shareName)

    if user.isRoot():
        # mount the share and hide its parent dir (/home/%user/media) in case it is not a hidden share
        return (_mountShare(username, networkPath, mountpoint, hideParentDir=not hiddenShare), mountpoint)
    else:
        # This will call mountShare() again with root privileges
        return (_mountShareWithoutRoot(networkPath, shareName, hiddenShare), mountpoint)

def getMountpointOfRemotePath(remoteFilePath, hiddenShare = False, username = None, autoMount = True):
    remoteFilePath = remoteFilePath.replace("\\", "/")

    if username == None:
        username = user.username()

    # get basepath fo remote file path
    # this turns //server/sysvol/linuxmuster.lan/Policies into //server/sysvol
    pattern = re.compile("(^\\/\\/[^\\/]+\\/[^\\/]+)")
    match = pattern.search(remoteFilePath)

    if match == None:
        logging.error("Cannot get local file path of {} beacuse it is not a valid path!".format(remoteFilePath))
        return False, None

    shareBasepath = match.group(0)
    if autoMount:
       mountShare(shareBasepath, hiddenShare=hiddenShare, username=username)
    
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

# --------------------
# - Helper functions -
# --------------------

def _mountShare(username, networkPath, mountpoint, hideParentDir=False):

    try:
        pwdInfo = pwd.getpwnam(username)
        uid = pwdInfo.pw_uid
        gid = pwdInfo.pw_gid
        #logging.info("user is: {0} uid is: {1} gid is: {2}".format(username, uid, gid))
        mountCommand = ("mount.cifs "
                "-o user={0},cruid={1},gid={2},uid={1},file_mode=0700,dir_mode=0700,sec=krb5,nodev,nosuid,mfsymlinks,nobrl,vers=3.0 "
                "'{3}' '{4}'")
    except KeyError:
        uid = -1
        gid = -1
        logging.warning("Uid could not be found! Continuing anyway!")
        logging.info("user is: {0}".format(username))
        mountCommand = ("mount.cifs "
                "-o user={0},file_mode=0700,dir_mode=0700,sec=krb5,nodev,nosuid,mfsymlinks,nobrl,vers=3.0 "
                "'{3}' '{4}'")

    logging.debug("Trying to mount {0} to {1}".format(networkPath, mountpoint))
    logging.debug("* Creating directory...")

    try:
        Path(mountpoint).mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        # Test if a share is already mounted there
        if _directoryIsMountpoint(mountpoint):
            logging.debug("* The mountpoint is already mounted.")
            # TODO: is this actually a success??
            return True
        else:
            logging.warning("* The target directory already exists, proceeding anyway!")

    mountCommand = mountCommand.format(username, uid, gid, networkPath, mountpoint)
    logging.debug("* Executing {} ".format(mountCommand))
    logging.debug("* Trying to mount...")
    if not os.system(mountCommand) == 0:
        logging.error("* Error mounting share!")
        return False

    logging.debug("* Success!")

    if hideParentDir:
        try:
            hiddenFilePath = "{}/../../.hidden".format(mountpoint)
            logging.debug("* hiding parent dir {}".format(hiddenFilePath))
            hiddenFile = open(hiddenFilePath, "w+")
            hiddenFile.write(mountpoint.split("/")[-2])
            hiddenFile.close()
        except:
            logging.warning("Could not hide parent dir of share {}".format(mountpoint))

    return True

def _unmountShare(mountpoint):
    # check if mountpoint exists
    if (not os.path.exists(mountpoint)) or (not os.path.isdir(mountpoint)):
        logging.warning("* Could not unmount {}, it does not exist.".format(mountpoint))

    # Try to unmount share
    logging.info("* Trying to unmount {0}...".format(mountpoint))
    if not os.system("umount '{0}'".format(mountpoint)) == 0:
        logging.warning("* Failed!")
        if _directoryIsMountpoint(mountpoint):
            logging("* It is still mounted! Exiting!")
            # Do not delete in this case! We might delete userdata!
            return
        logging("* It is not mounted! Continuing!")

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