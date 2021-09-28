import os, pwd, sys, shutil, re, subprocess, shutil
from linuxmusterLinuxclient7 import logging, constants, user, config, computer
from pathlib import Path

def mountShare(networkPath, shareName = None, hiddenShare = False, username = None):
    """
    Mount a given path of a samba share

    :param networkPath: Network path of the share
    :type networkPath: str
    :param shareName: The name of the share (name of the folder the share is being mounted to)
    :type shareName: str
    :param hiddenShare: If the share sould be visible in Nautilus
    :type hiddenShare: bool
    :param username: The user in whoms context the share should be mounted
    :type username: str
    :return: Tuple: (success, mountpoint)
    :rtype: tuple
    """
    networkPath = networkPath.replace("\\", "/")
    username = _getDefaultUsername(username)
    shareName = _getDefaultShareName(networkPath, shareName)

    if user.isRoot():
        return _mountShare(username, networkPath, shareName, hiddenShare, True)
    else:
        mountpoint = _getShareMountpoint(networkPath, username, hiddenShare, shareName)
        # This will call _mountShare() directly with root privileges
        return _mountShareWithoutRoot(networkPath, shareName, hiddenShare), mountpoint

def getMountpointOfRemotePath(remoteFilePath, hiddenShare = False, username = None, autoMount = True):
    """
    Get the local path of a remote samba share path.
    This function automatically checks if the shares is already mounted.
    It optionally automatically mounts the top path of the remote share:
    If the remote path is `//server/sysvol/linuxmuster.lan/Policies` it mounts `//server/sysvol`

    :param remoteFilePath: Remote path
    :type remoteFilePath: str
    :param hiddenShare: If the share sould be visible in Nautilus
    :type hiddenShare: bool
    :param username: The user in whoms context the share should be mounted
    :type username: str
    :parama autoMount: If the share should be mouted automatically if it is not already mounted
    :type autoMount: bool
    :return: Tuple: (success, mountpoint)
    :rtype: tuple
    """
    remoteFilePath = remoteFilePath.replace("\\", "/")
    username = _getDefaultUsername(username)

    # get basepath fo remote file path
    # this turns //server/sysvol/linuxmuster.lan/Policies into //server/sysvol
    pattern = re.compile("(^\\/\\/[^\\/]+\\/[^\\/]+)")
    match = pattern.search(remoteFilePath)

    if match is None:
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
    """
    Unmount all shares of a given user and safely delete the mountpoints and the parent directory.

    :param username: The username of the user
    :type username: str
    :return: True or False
    :rtype: bool
    """
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
            return False
        else:
            # Delete the directory
            logging.info("Deleting {0}...".format(shareMountBasedir))
            try:
                os.rmdir(shareMountBasedir)
            except Exception as e:
                logging.error("FAILED!")
                logging.exception(e)
                return False

    logging.info("===> Finished unmounting all shares of user {0} ===".format(username))
    return True

def getLocalSysvolPath():
    """
    Get the local mountpoint of the sysvol

    :return: Full path of the mountpoint
    :rtype: str
    """
    rc, networkConfig = config.network()
    if not rc:
        return False, None

    networkPath = f"//{networkConfig['serverHostname']}/sysvol"
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

    mountCommandOptions = f"file_mode=0700,dir_mode=0700,sec=krb5,nodev,nosuid,mfsymlinks,nobrl,vers=3.0,user={username}"
    rc, networkConfig = config.network()
    domain = None

    if rc:
        domain = networkConfig["domain"]
        mountCommandOptions += f",domain={domain.upper()}"

    try:
        pwdInfo = pwd.getpwnam(username)
        uid = pwdInfo.pw_uid
        gid = pwdInfo.pw_gid
        mountCommandOptions += f",gid={gid},uid={uid}"

        if not useCruidOfExecutingUser:
            mountCommandOptions += f",cruid={uid}"

    except KeyError:
        uid = -1
        gid = -1
        logging.warning("Uid could not be found! Continuing anyway!")

    mountCommand = [shutil.which("mount.cifs"), "-o", mountCommandOptions, networkPath, mountpoint]

    logging.debug(f"Trying to mount '{networkPath}' to '{mountpoint}'")
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

    logging.debug("* Executing '{}' ".format(" ".join(mountCommand)))
    logging.debug("* Trying to mount...")
    if not subprocess.call(mountCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
        logging.fatal(f"* Error mounting share {networkPath} to {mountpoint}!\n")
        return False, None

    logging.debug("* Success!")

    # hide the shares parent dir (/home/%user/media) in case it is not a hidden share
    if not hiddenShare:
        try:
            hiddenFilePath = f"{mountpoint}/../../.hidden"
            logging.debug(f"* hiding parent dir {hiddenFilePath}")
            hiddenFile = open(hiddenFilePath, "w+")
            hiddenFile.write(mountpoint.split("/")[-2])
            hiddenFile.close()
        except:
            logging.warning(f"Could not hide parent dir of share {mountpoint}")

    return True, mountpoint

def _unmountShare(mountpoint):
    # check if mountpoint exists
    if (not os.path.exists(mountpoint)) or (not os.path.isdir(mountpoint)):
        logging.warning(f"* Could not unmount {mountpoint}, it does not exist.")

    # Try to unmount share
    logging.info("* Trying to unmount {0}...".format(mountpoint))
    if not subprocess.call(["umount", mountpoint]) == 0:
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
        os.rmdir(mountpoint)
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

def _getDefaultShareName(networkPath, shareName=None):
    if shareName is None:
        shareName = networkPath.split("/")[-1]
    return shareName

def _mountShareWithoutRoot(networkPath, name, hidden):
    mountCommand = ["sudo", "/usr/share/linuxmuster-linuxclient7/scripts/sudoTools", "mount-share", "--path", networkPath, "--name", name]

    if hidden:
        mountCommand.append("--hidden")

    return subprocess.call(mountCommand) == 0

def _getShareMountpoint(networkPath, username, hidden, shareName = None):
    logging.debug(f"Calculating mountpoint of {networkPath}")

    shareName = _getDefaultShareName(networkPath, shareName)

    if hidden:
        return "{0}/{1}".format(constants.hiddenShareMountBasepath.format(username), shareName)
    else:
        return "{0}/{1}".format(constants.shareMountBasepath.format(username), shareName)

def _directoryIsMountpoint(dir):
    return subprocess.call(["mountpoint", "-q", dir]) == 0
