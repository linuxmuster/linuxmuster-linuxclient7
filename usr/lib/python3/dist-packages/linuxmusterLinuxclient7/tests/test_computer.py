from subprocess import CompletedProcess
from unittest import mock
from .. import computer
import os

@mock.patch("linuxmusterLinuxclient7.computer.socket.gethostname")
def test_hostname(mockSocketGetHostname):
    mockSocketGetHostname.return_value = "computer1.linuxmuster.lan"
    assert computer.hostname() == "computer1"

@mock.patch("linuxmusterLinuxclient7.computer.hostname")
def test_hostnameIsValid(mockHostname):
    mockHostname.return_value = "computer1"
    assert computer.hostnameIsValid()
    mockHostname.return_value = "aabk-r100-pc012"
    assert computer.hostnameIsValid()
    mockHostname.return_value = "aabk-r100-pc0123"
    assert not computer.hostnameIsValid()

@mock.patch("linuxmusterLinuxclient7.computer._setLoginScreenWarning")
@mock.patch("linuxmusterLinuxclient7.computer.hostname")
def test_checkHostname(mockHostname, mockSetLoginScreenWarning):
    mockHostname.return_value = "computer1"
    assert computer.checkHostname()
    assert mockSetLoginScreenWarning.call_args.args[0] is None

    mockHostname.return_value = "aabk-r100-pc0123"
    assert not computer.checkHostname()
    assert "aabk-r100-pc0123" in mockSetLoginScreenWarning.call_args.args[0]

@mock.patch("linuxmusterLinuxclient7.computer._userIsLoggedIn")
@mock.patch("linuxmusterLinuxclient7.computer.subprocess.call")
def test_setLoginScreenWarning(mockSubprocessCall, mockUserIsLoggedIn, tmp_path):
    warningFile = str(tmp_path / "95-linuxmuster-linuxclient7")
    mockUserIsLoggedIn.return_value = False

    with mock.patch("linuxmusterLinuxclient7.computer.constants.gdmDconfDir", str(tmp_path)), mock.patch("linuxmusterLinuxclient7.computer.constants.loginScreenWarningFile", warningFile):
        assert not computer._setLoginScreenWarning(None)
        assert mockSubprocessCall.call_count == 0

        assert computer._setLoginScreenWarning("Hostname too long")
        with open(warningFile) as file:
            content = file.read()
        assert "banner-message-enable=true" in content
        assert 'banner-message-text="Hostname too long"' in content
        assert ["systemctl", "try-restart", "gdm"] in [c.args[0] for c in mockSubprocessCall.call_args_list]

        mockSubprocessCall.reset_mock()
        assert not computer._setLoginScreenWarning("Hostname too long")
        assert mockSubprocessCall.call_count == 0

        mockUserIsLoggedIn.return_value = True
        assert computer._setLoginScreenWarning(None)
        assert not os.path.exists(warningFile)
        assert ["systemctl", "try-restart", "gdm"] not in [c.args[0] for c in mockSubprocessCall.call_args_list]

    with mock.patch("linuxmusterLinuxclient7.computer.constants.gdmDconfDir", str(tmp_path / "missing")):
        assert not computer._setLoginScreenWarning("Hostname too long")

@mock.patch("linuxmusterLinuxclient7.computer.subprocess.run")
def test_userIsLoggedIn(mockSubprocessRun):
    mockSubprocessRun.return_value = CompletedProcess(args=[], returncode=0, stdout="60578 gdm-greeter no active\n")
    assert not computer._userIsLoggedIn()

    mockSubprocessRun.return_value = CompletedProcess(args=[], returncode=0, stdout="60578 gdm-greeter no active\n1662401376 yukigrun no active\n")
    assert computer._userIsLoggedIn()

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