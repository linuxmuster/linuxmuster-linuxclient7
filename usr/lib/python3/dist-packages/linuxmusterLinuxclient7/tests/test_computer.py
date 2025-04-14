from unittest import mock
from .. import computer

@mock.patch("linuxmusterLinuxclient7.computer.socket.gethostname")
def test_hostname(mockSocketGetHostname):
    mockSocketGetHostname.return_value = "computer1.linuxmuster.lan"
    assert computer.hostname() == "computer1"

@mock.patch("linuxmusterLinuxclient7.computer.hostname")
def test_krbHostName(mockHostname):
    mockHostname.return_value = "computer1"
    assert computer.krbHostName() == "COMPUTER1$"

@mock.patch("linuxmusterLinuxclient7.computer.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.computer.hostname")
def test_readAttributes(mockHostname, mockLdapHelperSearchOne):
    mockHostname.return_value = "computer1"
    mockLdapHelperSearchOne.return_value = (True, {
        "Attribute": "Value"
    })

    rc, attributes = computer.readAttributes()
    assert rc
    assert mockLdapHelperSearchOne.call_args.args[0].lower() == "(samaccountname=computer1$)"
    assert attributes["Attribute"] == "Value"

    mockLdapHelperSearchOne.return_value = (False, None)
    rc, attributes = computer.readAttributes()
    assert not rc
    assert attributes is None
    

@mock.patch("linuxmusterLinuxclient7.computer.localUserHelper.getGroupsOfLocalUser")
@mock.patch("linuxmusterLinuxclient7.computer.hostname")
def test_isInGroup(mockHostname, mockLocalUserHelperGetGroupsOfLocalUser):
    mockHostname.return_value = "computer1"

    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (True, ["group1", "group2"])
    assert computer.isInGroup("group1")
    assert computer.isInGroup("group2")
    assert not computer.isInGroup("group3")

    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (False, ["group1", "group2"])
    assert not computer.isInGroup("group1")
    assert not computer.isInGroup("group2")
    assert not computer.isInGroup("group3")


    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (True, [])
    assert not computer.isInGroup("group1")
    assert not computer.isInGroup("group2")
    assert not computer.isInGroup("group3")

    assert mockLocalUserHelperGetGroupsOfLocalUser.call_args.args[0] == computer.krbHostName()

@mock.patch("linuxmusterLinuxclient7.computer.localUserHelper.getGroupsOfLocalUser")
@mock.patch("linuxmusterLinuxclient7.computer.hostname")
def test_isInAD(mockHostname, mockLocalUserHelperGetGroupsOfLocalUser):
    mockHostname.return_value = "computer1"

    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (True, ["domain computers"])
    assert computer.isInAD()

    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (True, ["group1"])
    assert not computer.isInAD()

    mockLocalUserHelperGetGroupsOfLocalUser.return_value = (False, ["domain computers"])
    assert not computer.isInAD()

    assert mockLocalUserHelperGetGroupsOfLocalUser.call_args.args[0] == computer.krbHostName()