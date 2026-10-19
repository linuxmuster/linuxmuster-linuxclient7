from unittest import mock
from .. import setup

@mock.patch("linuxmusterLinuxclient7.setup.realm.clearUserCache")
@mock.patch("linuxmusterLinuxclient7.setup.computer.checkHostname")
def test_setupInvalidHostname(mockCheckHostname, mockClearUserCache):
    mockCheckHostname.return_value = False
    assert not setup.setup()
    assert mockClearUserCache.call_count == 0

@mock.patch("linuxmusterLinuxclient7.setup._checkSssdKrb5ChildCaps")
@mock.patch("linuxmusterLinuxclient7.setup.computer.checkHostname")
@mock.patch("linuxmusterLinuxclient7.setup.isSetup")
def test_statusInvalidHostname(mockIsSetup, mockCheckHostname, mockCheckSssdKrb5ChildCaps):
    mockIsSetup.return_value = True
    mockCheckHostname.return_value = False
    assert not setup.status()
    assert mockCheckSssdKrb5ChildCaps.call_count == 0
