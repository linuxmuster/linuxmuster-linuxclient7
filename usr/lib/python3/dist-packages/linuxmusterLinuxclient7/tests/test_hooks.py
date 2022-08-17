from email.mime import base
from pathlib import Path
from unittest import mock
from .. import hooks, fileHelper
import pytest, os

@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.config.network")
@mock.patch("linuxmusterLinuxclient7.hooks.user.readAttributes")
@mock.patch("linuxmusterLinuxclient7.hooks.computer.readAttributes")
@mock.patch("linuxmusterLinuxclient7.hooks.shares.getLocalSysvolPath")
@mock.patch("linuxmusterLinuxclient7.hooks.constants.etcBaseDir", "/tmp/hooks")
@pytest.mark.parametrize("hook", [hooks.Type.Boot, hooks.Type.Shutdown, hooks.Type.LoginAsRoot, hooks.Type.Login, hooks.Type.SessionStarted, hooks.Type.LogoutAsRoot, hooks.Type.LoginLogoutAsRoot])
def test_runHook(mockSharesGetLocalSysvolPath, mockComputerAttributes, mockUserAttributes, mockConfigNetwork, mockSubprocessCall, hook):

    # mock ennvironment
    mockConfigNetwork.return_value = (True, {"domain": "linuxmuster.lan"})
    mockUserAttributes.return_value = (True, {"sophomorixSchoolname": "default-school"})
    mockComputerAttributes.return_value = (True, {"sophomorixSchoolname": "default-school"})
    mockSharesGetLocalSysvolPath.return_value = (True, "/tmp/sysvol")

    hookScripts = _createLocalHookScripts(hook)
    hookScripts = hookScripts + _createRemoteHookScripts(hook)

    hooks.runHook(hook)

    calls = []
    for i in range(len(mockSubprocessCall.call_args_list)):
        firstArg = mockSubprocessCall.call_args_list[i].args[0][0]
        if not firstArg in calls:
            calls.append(firstArg)

    for script in hookScripts:
        assert script in calls

    fileHelper.deleteDirectory("/tmp/hooks")
    fileHelper.deleteDirectory("/tmp/sysvol")

@pytest.mark.parametrize("hook", [hooks.Type.Boot, hooks.Type.Shutdown, hooks.Type.LoginAsRoot, hooks.Type.Login, hooks.Type.SessionStarted, hooks.Type.LogoutAsRoot, hooks.Type.LoginLogoutAsRoot])
def test_getLocalHookScript(hook):
    assert hooks.getLocalHookScript(hook) == f"/usr/share/linuxmuster-linuxclient7/scripts/on{hook.name}"

@mock.patch("linuxmusterLinuxclient7.hooks.user.isUserInAD")
@mock.patch("linuxmusterLinuxclient7.hooks.user.username")
@mock.patch("linuxmusterLinuxclient7.hooks.computer.isInAD")
@mock.patch("linuxmusterLinuxclient7.hooks.setup.isSetup")
def test_shouldHooksBeExecuted(mockSetupIsSetup, mockComputerIsInAD, mockUserUsername, mockUserIsUserInAD):
    mockSetupIsSetup.return_value = True
    mockComputerIsInAD.return_value = True
    mockUserUsername.return_value = "user1"
    mockUserIsUserInAD.return_value = True

    assert hooks.shouldHooksBeExecuted()
    assert mockUserIsUserInAD.call_args.args[0] == "user1"

    assert hooks.shouldHooksBeExecuted("user2")
    assert mockUserIsUserInAD.call_args.args[0] == "user2"

    mockSetupIsSetup.return_value = False
    assert not hooks.shouldHooksBeExecuted()

    mockSetupIsSetup.return_value = True
    mockComputerIsInAD.return_value = False
    assert not hooks.shouldHooksBeExecuted()

    mockComputerIsInAD.return_value = True
    mockUserIsUserInAD.return_value = False
    assert not hooks.shouldHooksBeExecuted()


# --------------------
# - Helper functions -
# --------------------

def _createLocalHookScripts(hook, basedir="/tmp/hooks"):
    try:
        os.mkdir(basedir)
    except FileExistsError:
        pass

    try:
        os.mkdir(f"{basedir}/on{hook.name}.d")
    except FileExistsError:
        pass

    createdFiles = []
    for i in range(2):
        thisFile = f"{basedir}/on{hook.name}.d/script-{i}"
        with open(thisFile, "w") as file:
            file.write("#!/bin/bash\necho \"test-{i}\"")
        os.chmod(thisFile, 0o777)
        createdFiles.append(thisFile)

    return createdFiles

def _createRemoteHookScripts(hook, sysvolPath="/tmp/sysvol", domain="linuxmuster.lan", school="default-school"):
    if not hook in hooks.remoteScriptNames:
        return []

    hookScriptPathTemplate = "{0}/{1}/scripts/{2}/{3}/linux/{4}".format(sysvolPath, domain, school, "{}", hooks.remoteScriptNames[hook])

    createdFiles = []
    for hookKind in ["lmn", "custom"]:
        hookScriptPath = hookScriptPathTemplate.format(hookKind)
        hookDir = os.path.dirname(hookScriptPath)
        Path(hookDir).mkdir(parents=True, exist_ok=True)

        with open(hookScriptPath, "w") as file:
            file.write("#!/bin/bash\necho \"test-{i}\"")
        os.chmod(hookScriptPath, 0o777)
        createdFiles.append(hookScriptPath)

    return createdFiles