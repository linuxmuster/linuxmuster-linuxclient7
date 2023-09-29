from subprocess import CompletedProcess
from unittest import mock
from .. import shares

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