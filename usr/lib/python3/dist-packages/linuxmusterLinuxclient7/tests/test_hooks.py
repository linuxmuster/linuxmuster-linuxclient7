from unittest import mock
from .. import hooks, fileHelper
import pytest, os

@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.constants.etcBaseDir", "/tmp/hooks")
@pytest.mark.parametrize("hook", [hooks.Type.Boot, hooks.Type.Shutdown, hooks.Type.LoginAsRoot, hooks.Type.Login, hooks.Type.SessionStarted, hooks.Type.LogoutAsRoot, hooks.Type.LoginLogoutAsRoot])
def test_runHook(mockSubprocessCall,hook):
    try:
        os.mkdir("/tmp/hooks")
    except FileExistsError:
        pass

    try:
        os.mkdir(f"/tmp/hooks/on{hook.name}.d")
    except FileExistsError:
        pass

    for i in range(2):
        with open(f"/tmp/hooks/on{hook.name}.d/script-{i}", "w") as file:
            file.write("#!/bin/bash\necho \"test-{i}\"")
        os.chmod(f"/tmp/hooks/on{hook.name}.d/script-{i}", 0o777)
        
    hooks.runHook(hook)

    calls = []
    for i in range(len(mockSubprocessCall.call_args_list)):
        firstArg = mockSubprocessCall.call_args_list[i].args[0][0]
        if not firstArg in calls:
            calls.append(firstArg)

    for i in range(2):
        assert f"/tmp/hooks/on{hook.name}.d/script-{i}" in calls

    fileHelper.deleteDirectory("/tmp/hooks")

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