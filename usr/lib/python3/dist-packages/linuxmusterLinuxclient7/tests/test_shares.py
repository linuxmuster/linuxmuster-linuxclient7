from subprocess import CompletedProcess
from unittest import mock
from .. import shares

def test_networkPathIsValid():
    assert shares._networkPathIsValid("//server/sysvol")
    assert shares._networkPathIsValid("//server/share/subdir")
    assert not shares._networkPathIsValid("")
    assert not shares._networkPathIsValid("/server/share")
    assert not shares._networkPathIsValid("//server")
    assert not shares._networkPathIsValid("//server/")
    assert not shares._networkPathIsValid("//server/../etc")
    assert not shares._networkPathIsValid("//server/share\nfoo")

def test_shareNameIsValid():
    assert shares._shareNameIsValid("sysvol")
    assert shares._shareNameIsValid("My Share (H:)")
    assert not shares._shareNameIsValid("")
    assert not shares._shareNameIsValid(None)
    assert not shares._shareNameIsValid(".")
    assert not shares._shareNameIsValid("..")
    assert not shares._shareNameIsValid("../../etc/cron.d")
    assert not shares._shareNameIsValid("a/b")
    assert not shares._shareNameIsValid("a\\b")

def test_mountpointIsWithinBase():
    assert shares._mountpointIsWithinBase("/home/user1/media/share", "user1", False)
    assert shares._mountpointIsWithinBase("/srv/samba/user1/share", "user1", True)
    assert not shares._mountpointIsWithinBase("/home/user1/media", "user1", False)
    assert not shares._mountpointIsWithinBase("/home/user1/media/../../../etc/cron.d", "user1", False)
    assert not shares._mountpointIsWithinBase("/etc/cron.d", "user1", False)

@mock.patch("subprocess.call")
def test_mountShareRejectsInvalidInput(mockSubprocessCall):
    assert shares._mountShare("user1", "//server/share", "../../../../etc/cron.d", False, False) == (False, None)
    assert shares._mountShare("user1", "//server/../etc", "share", False, False) == (False, None)
    for callArgs in mockSubprocessCall.call_args_list:
        assert callArgs.args[0][0] == "logger"

@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.shares._getShareMountpoint")
def test_mountShareRejectsMountpointOutsideBase(mockGetShareMountpoint, mockSubprocessCall):
    mockGetShareMountpoint.return_value = "/etc/cron.d"
    assert shares._mountShare("user1", "//server/share", "share", False, False) == (False, None)
    for callArgs in mockSubprocessCall.call_args_list:
        assert callArgs.args[0][0] == "logger"

@mock.patch("linuxmusterLinuxclient7.shares.mountShare")
@mock.patch("linuxmusterLinuxclient7.shares.computer.hostname")
@mock.patch("linuxmusterLinuxclient7.shares.user.isRoot")
@mock.patch("linuxmusterLinuxclient7.shares.user.username")
def test_getMountpointOfRemotePath(mockUserUsername, mockUserIsRoot, mockComputerHostname, mockSharesMountShare):
    mockUserIsRoot.return_value = False
    mockUserUsername.return_value = "user2"
    mockComputerHostname.return_value = "COMPUTER1"
    mockSharesMountShare.return_value = (True, "/srv/samba/user1/sysvol")

    res = shares.getMountpointOfRemotePath("//server/sysvol/linuxmuster.lan/Policies", hiddenShare=False, username="user1", autoMount=False)
    assert res == (True, "/home/user1/media/sysvol/linuxmuster.lan/Policies")

    res = shares.getMountpointOfRemotePath("//server/sysvol/linuxmuster.lan/Policies", hiddenShare=True, username="user1", autoMount=False)
    assert res == (True, "/srv/samba/user1/sysvol/linuxmuster.lan/Policies")

    res = shares.getMountpointOfRemotePath("//server/", hiddenShare=True, username="user1", autoMount=False)
    assert res == (False, None)

    # test with default username
    res = shares.getMountpointOfRemotePath("//server/sysvol/linuxmuster.lan/Policies", hiddenShare=False, autoMount=False)
    assert res == (True, "/home/user2/media/sysvol/linuxmuster.lan/Policies")

    res = shares.getMountpointOfRemotePath("//server/sysvol/linuxmuster.lan/Policies", hiddenShare=True, autoMount=False)
    assert res == (True, "/srv/samba/user2/sysvol/linuxmuster.lan/Policies")

    # test with root
    mockUserIsRoot.return_value = True
    res = shares.getMountpointOfRemotePath("//server/sysvol/linuxmuster.lan/Policies", hiddenShare=False, autoMount=False)
    assert res == (False, None)

    res = shares.getMountpointOfRemotePath("//server/sysvol/linuxmuster.lan/Policies", hiddenShare=True, autoMount=False)
    assert res == (True, "/srv/samba/COMPUTER1$/sysvol/linuxmuster.lan/Policies")

    # test with autoMount
    res = shares.getMountpointOfRemotePath("//server/sysvol/linuxmuster.lan/Policies", hiddenShare=False, username="user1", autoMount=True)
    assert res == (True, "/home/user1/media/sysvol/linuxmuster.lan/Policies")
    assert mockSharesMountShare.call_count == 1
    assert mockSharesMountShare.call_args == mock.call('//server/sysvol', hiddenShare=False, username='user1')

    res = shares.getMountpointOfRemotePath("//server/sysvol/linuxmuster.lan/Policies", hiddenShare=True, username="user1", autoMount=True)
    assert res == (True, "/srv/samba/user1/sysvol/linuxmuster.lan/Policies")
    assert mockSharesMountShare.call_count == 2
    assert mockSharesMountShare.call_args == mock.call('//server/sysvol', hiddenShare=True, username='user1')


    mockSharesMountShare.return_value = (False, None)
    res = shares.getMountpointOfRemotePath("//server/sysvol/linuxmuster.lan/Policies", hiddenShare=False, username="user1", autoMount=True)
    assert res == (False, None)
    assert mockSharesMountShare.call_count == 3
    assert mockSharesMountShare.call_args == mock.call('//server/sysvol', hiddenShare=False, username='user1')