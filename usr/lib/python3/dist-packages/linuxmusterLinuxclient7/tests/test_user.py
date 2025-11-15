from unittest import mock
from .. import user

@mock.patch("linuxmusterLinuxclient7.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.user.user.username")
@mock.patch("linuxmusterLinuxclient7.user.user.isInAD")
def test_readAttributes(mockUserIsInAD, mockUserUsername, mockLdapHelperSearchOne):
    mockUserIsInAD.return_value = False
    assert not user.readAttributes()[0]

    mockUserIsInAD.return_value = True
    mockUserUsername.return_value = "user1"
    mockLdapHelperSearchOne.return_value = (True, {
        "Attribute": "Value"
    })

    rc, attributes = user.readAttributes()
    assert rc
    assert mockLdapHelperSearchOne.call_args.args[0].lower() == "(samaccountname=user1)"
    assert attributes["Attribute"] == "Value"

@mock.patch("linuxmusterLinuxclient7.user.readAttributes")
def test_school(mockReadAttributes):
    mockReadAttributes.return_value = (False, None)
    assert not user.school()[0]

    mockReadAttributes.return_value = (True, {
        "sophomorixSchoolname": "school1"
    })
    assert user.school() == (True, "school1")

@mock.patch("linuxmusterLinuxclient7.user.getpass.getuser")
def test_username(mockGetpassGetuser):
    mockGetpassGetuser.return_value = "user1"
    assert user.username() == "user1"

    mockGetpassGetuser.return_value = "USER1"
    assert user.username() == "user1"

@mock.patch("linuxmusterLinuxclient7.user.computer.isInAD")
@mock.patch("linuxmusterLinuxclient7.user.localUserHelper.getGroupsOfLocalUser")
def test_isUserInAD(mockLocalUserHelperGetGroupsOfLocalUser, mockComputerIsInAD):
    mockComputerIsInAD.return_value = False
    assert not user.isUserInAD("user1")

    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (False, None)
    mockComputerIsInAD.return_value = True
    assert not user.isUserInAD("user1")

    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (True, ["group1"])
    mockComputerIsInAD.return_value = True
    assert not user.isUserInAD("user1")
    assert mockLocalUserHelperGetGroupsOfLocalUser.call_args.args[0] == "user1"

    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (True, ["domain users"])
    mockComputerIsInAD.return_value = True
    assert user.isUserInAD("user1")
    assert mockLocalUserHelperGetGroupsOfLocalUser.call_args.args[0] == "user1"

@mock.patch("linuxmusterLinuxclient7.user.username")
@mock.patch("linuxmusterLinuxclient7.user.isUserInAD")
def test_isInAD(mockIsUserInAD, mockUsername):
    mockIsUserInAD.return_value = False
    mockUsername.return_value = "user1"
    assert not user.isInAD()
    assert mockIsUserInAD.call_args.args[0] == "user1"

    mockIsUserInAD.return_value = True
    mockUsername.return_value = "user1"
    assert user.isInAD()
    assert mockIsUserInAD.call_args.args[0] == "user1"

@mock.patch("linuxmusterLinuxclient7.user.os.geteuid")
def test_isRoot(mockOsGeteuid):
    mockOsGeteuid.return_value = 0
    assert user.isRoot()

    mockOsGeteuid.return_value = 1
    assert not user.isRoot()

@mock.patch("linuxmusterLinuxclient7.user.localUserHelper.getGroupsOfLocalUser")
@mock.patch("linuxmusterLinuxclient7.user.username")
def test_isInGroup(mockUsername, mockLocalUserHelperGetGroupsOfLocalUser):
    mockUsername.return_value = "user1"

    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (True, ["group1", "group2"])
    assert user.isInGroup("group1")
    assert user.isInGroup("group2")
    assert not user.isInGroup("group3")

    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (False, ["group1", "group2"])
    assert not user.isInGroup("group1")
    assert not user.isInGroup("group2")
    assert not user.isInGroup("group3")


    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (True, [])
    assert not user.isInGroup("group1")
    assert not user.isInGroup("group2")
    assert not user.isInGroup("group3")

    assert mockLocalUserHelperGetGroupsOfLocalUser.call_args.args[0] == "user1"

@mock.patch("linuxmusterLinuxclient7.user.constants.gtkBookmarksFile", "/tmp/{}-bookmarks")
@mock.patch("linuxmusterLinuxclient7.user.username")
def test_cleanTemplateUserGtkBookmarks(mockUsername):
    mockUsername.return_value = "user1"

    with open("/tmp/user1-bookmarks", "w") as originalFile:
        originalFile.write("line1\nlinuxadmin line2\nline3")

    assert user.cleanTemplateUserGtkBookmarks()
    
    with open("/tmp/user1-bookmarks", "r") as originalFile:
        newContents = originalFile.read()
        assert "linuxadmin" not in newContents and "line2" not in newContents

@mock.patch("linuxmusterLinuxclient7.user.constants.gtkBookmarksFile", "/tmp")
def test_cleanTemplateUserGtkBookmarks_unwritableFile():
    assert not user.cleanTemplateUserGtkBookmarks()

@mock.patch("linuxmusterLinuxclient7.user.readAttributes")
@mock.patch("linuxmusterLinuxclient7.user.username")
def test_getHomeShareMountpoint(mockUsername, mockReadAttributes):
    mockUsername.return_value = "user1"
    mockReadAttributes.return_value = (False, None)
    assert not user.getHomeShareMountpoint()[0]

    # homeDrive missing from attributes
    mockReadAttributes.return_value = (True, {})
    assert not user.getHomeShareMountpoint()[0]


    mockReadAttributes.return_value = (True, {"homeDrive": "H:"})
    rc, homeShareMountpoint = user.getHomeShareMountpoint()
    assert rc
    assert homeShareMountpoint == "/home/user1/media/user1 (H:)"


@mock.patch("linuxmusterLinuxclient7.gpo.config.shares")
@mock.patch("linuxmusterLinuxclient7.user.readAttributes")
@mock.patch("linuxmusterLinuxclient7.user.username")
def test_getHomeShareMountpointCustomShareNameTemplate(mockUsername, mockReadAttributes, mockConfigShares):
    mockUsername.return_value = "user1"
    mockReadAttributes.return_value = (True, {"homeDrive": "H:"})
    mockConfigShares.return_value = {
        "nameTemplate": "{label}_{letter}"
    }

    rc, homeShareMountpoint = user.getHomeShareMountpoint()
    assert rc
    assert homeShareMountpoint == "/home/user1/media/user1_H"

    # Test without letter
    mockConfigShares.return_value = {
        "nameTemplate": "{label}"
    }
    rc, homeShareMountpoint = user.getHomeShareMountpoint()
    assert rc
    assert homeShareMountpoint == "/home/user1/media/user1"
    
@mock.patch("linuxmusterLinuxclient7.user.shares.mountShare")
@mock.patch("linuxmusterLinuxclient7.user.readAttributes")
@mock.patch("linuxmusterLinuxclient7.user.username")
def test_mountHomeShare(mockUsername, mockReadAttributes, mockSharesMountShare):
    mockUsername.return_value = "user1"
    mockReadAttributes.return_value = (False, None)
    assert not user.mountHomeShare()[0]

    mockReadAttributes.return_value = (True, {})
    assert not user.mountHomeShare()[0]

    mockReadAttributes.return_value = (True, {"homeDrive": "H:"})
    assert not user.mountHomeShare()[0]

    mockReadAttributes.return_value = (True, {"homeDrive": "H:", "homeDirectory": "user1"})
    mockSharesMountShare.return_value = (False, None)
    assert not user.mountHomeShare()[0]

    mockReadAttributes.return_value = (True, {"homeDrive": "H:", "homeDirectory": "user1"})
    mockSharesMountShare.return_value = (True, "mountpoint")
    rc, mountpoint = user.mountHomeShare()
    assert rc
    assert mountpoint == "mountpoint"
    assert mockSharesMountShare.call_args == mock.call('user1', shareName='user1 (H:)', hiddenShare=False, username='user1')

