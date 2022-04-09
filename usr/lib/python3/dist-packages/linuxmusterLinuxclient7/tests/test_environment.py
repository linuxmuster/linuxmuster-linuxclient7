from unittest import mock
from .. import environment, fileHelper
import os
import ctypes

@mock.patch('linuxmusterLinuxclient7.environment.constants.tmpEnvironmentFilePath', "/tmp/env")
@mock.patch("linuxmusterLinuxclient7.environment.user.isInAD")
def test_export(mockUserIsInAD):
    fileHelper.deleteFile("/tmp/env")

    mockUserIsInAD.return_value = False
    assert not environment.export("Key=Value")

    mockUserIsInAD.return_value = True
    os.environ["LinuxmusterLinuxclient7EnvFixActive"] = "0"
    assert not environment.export("Key=Value")

    os.environ["LinuxmusterLinuxclient7EnvFixActive"] = "1"
    assert environment.export("Key1=Value1")
    
    # check content of tmp file
    with open("/tmp/env", "r") as tmpEnvironmentFile:
        assert "export 'Key1=Value1'" in tmpEnvironmentFile.read()

@mock.patch('linuxmusterLinuxclient7.environment.constants.tmpEnvironmentFilePath', "/tmp")
@mock.patch("linuxmusterLinuxclient7.environment.user.isInAD")
def test_exportUnwritableTmpfile(mockUserIsInAD):
    mockUserIsInAD.return_value = True
    os.environ["LinuxmusterLinuxclient7EnvFixActive"] = "1"
    assert not environment.export("Key=Value")

@mock.patch('linuxmusterLinuxclient7.environment.constants.tmpEnvironmentFilePath', "/tmp/env")
@mock.patch("linuxmusterLinuxclient7.environment.user.isInAD")
def test_unset(mockUserIsInAD):
    fileHelper.deleteFile("/tmp/env")
    mockUserIsInAD.return_value = True
    os.environ["LinuxmusterLinuxclient7EnvFixActive"] = "1"

    environment.unset("Key")

    with open("/tmp/env", "r") as tmpEnvironmentFile:
        assert "unset 'Key'" in tmpEnvironmentFile.read()