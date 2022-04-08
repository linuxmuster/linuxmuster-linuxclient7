from unittest import mock
from .. import localUserHelper

@mock.patch("linuxmusterLinuxclient7.localUserHelper.subprocess.check_output")
def test_getGroupsOfLocalUserOk(mockOutput):
    mockOutput.return_value = b"group1\x00group2\x00"

    rc, groups = localUserHelper.getGroupsOfLocalUser("user1")
    
    assert rc 
    assert "user1" in mockOutput.call_args.args[0]
    assert "group1" in groups and "group2" in groups


@mock.patch("linuxmusterLinuxclient7.localUserHelper.subprocess.check_output")
def test_getGroupsOfLocalUserError(mockOutput):
    mockOutput.return_value = None

    rc, groups = localUserHelper.getGroupsOfLocalUser("user1")

    assert not rc