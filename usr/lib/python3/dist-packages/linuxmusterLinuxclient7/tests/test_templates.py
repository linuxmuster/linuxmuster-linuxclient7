from pathlib import Path
from unittest import mock
from .. import templates, fileHelper
import pytest, os

@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.config.network")
@mock.patch("linuxmusterLinuxclient7.templates.constants.configFileTemplateDir", f"{os.path.dirname(os.path.realpath(__file__))}/files/templates")
def test_applyAll(mockConfigNetwork, mockSubprocessCall):
    mockConfigNetwork.return_value = (True, {"serverHostname": "linuxmuster.lan", "domain": "linuxmuster.lan", "realm": "LINUXMUSTER"})
    mockSubprocessCall.return_value = 0

    assert templates.applyAll()

    assert sorted(os.listdir("/tmp/templates")) == ["01-applied.conf", "02-applied", "03-applied.xml"]

    # open files and check content
    with open("/tmp/templates/01-applied.conf", "r") as f:
        content = f.read()
        assert content == """

# serverHostname
serverHostname="linuxmuster.lan"
# domain
domain="linuxmuster.lan"
# realm
realm="LINUXMUSTER"
# userTemplateDir
userTemplateDir="/home/linuxadmin"
# hiddenShareMountBasepath
hiddenShareMountBasepath="/srv/samba/%(USER)"
# hookScriptBoot
hookScriptBoot="/usr/share/linuxmuster-linuxclient7/scripts/onBoot"
# hookScriptShutdown
hookScriptShutdown="/usr/share/linuxmuster-linuxclient7/scripts/onShutdown"
# hookScriptLoginLogoutAsRoot
hookScriptLoginLogoutAsRoot="/usr/share/linuxmuster-linuxclient7/scripts/onLoginLogoutAsRoot"
# hookScriptSessionStarted
hookScriptSessionStarted="/usr/share/linuxmuster-linuxclient7/scripts/onSessionStarted"
"""

    with open("/tmp/templates/02-applied", "r") as f:
        content = f.read()
        assert content == """

/home/linuxadmin@/usr/share/linuxmuster-linuxclient7/scripts/onBoot/usr/share/linuxmuster-linuxclient7/scripts/onSessionStarted@@@@ @@@
"""

    with open("/tmp/templates/03-applied.xml", "r") as f:
        content = f.read()
        assert content == """<config>
    <serverHostname>linuxmuster.lan</serverHostname>
    <userTemplateDir>/home/linuxadmin</userTemplateDir>
    <hookScriptShutdown>/usr/share/linuxmuster-linuxclient7/scripts/onShutdown</hookScriptShutdown>
</config>
"""
    systemctlFound = False
    for call_args in mockSubprocessCall.call_args_list:
        if call_args[0][0] == ["systemctl", "daemon-reload"]:
            systemctlFound = True
            break

    assert systemctlFound

    fileHelper.deleteDirectory("/tmp/templates")

@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.config.network")
@mock.patch("linuxmusterLinuxclient7.templates.constants.configFileTemplateDir", f"{os.path.dirname(os.path.realpath(__file__))}/files/templates")
def test_applyAllError(mockConfigNetwork, mockSubprocessCall):
    mockConfigNetwork.return_value = (False, None)
    mockSubprocessCall.return_value = 0
    assert not templates.applyAll()


    mockConfigNetwork.return_value = (True, {"serverHostname": "linuxmuster.lan", "domain": "linuxmuster.lan", "realm": "LINUXMUSTER"})
    mockSubprocessCall.return_value = 1
    assert not templates.applyAll()

    mockConfigNetwork.return_value = (True, {"serverHostname": "linuxmuster.lan", "domain": "linuxmuster.lan"})
    mockSubprocessCall.return_value = 0
    assert not templates.applyAll()

    fileHelper.deleteDirectory("/tmp/templates")