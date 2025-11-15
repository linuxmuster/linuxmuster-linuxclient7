from pathlib import Path
from unittest import mock
from .. import hooks, fileHelper
import pytest, os

@mock.patch("linuxmusterLinuxclient7.hooks.config.network")
@mock.patch("linuxmusterLinuxclient7.hooks.user.readAttributes")
@mock.patch("linuxmusterLinuxclient7.hooks.computer.readAttributes")
@mock.patch("linuxmusterLinuxclient7.hooks.shares.getLocalSysvolPath")
@mock.patch("linuxmusterLinuxclient7.hooks.constants.etcBaseDir", "/tmp/hooks")
@pytest.mark.parametrize("hook", [hooks.Type.Boot, hooks.Type.Shutdown, hooks.Type.LoginAsRoot, hooks.Type.Login, hooks.Type.SessionStarted, hooks.Type.LogoutAsRoot, hooks.Type.LoginLogoutAsRoot])
def test_runHook(mockSharesGetLocalSysvolPath, mockComputerAttributes, mockUserAttributes, mockConfigNetwork, hook):

    # mock ennvironment
    mockConfigNetwork.return_value = (True, {"domain": "linuxmuster.lan"})
    mockUserAttributes.return_value = (True, {"sophomorixSchoolname": "default-school", "sophomorxCustomMulti1": ["test1", "test2"]})
    mockComputerAttributes.return_value = (True, {"sophomorixSchoolname": "default-school"})
    mockSharesGetLocalSysvolPath.return_value = (True, "/tmp/sysvol")

    hookScripts = _createLocalHookScripts(hook)
    hookScripts = hookScripts + _createRemoteHookScripts(hook)

    hooks.runHook(hook)

    lastExecutionTimestamp = 0
    for script in hookScripts:
        with open(f"{script}-env", "r") as file:
            env = file.read()

        env = env.split("\n")
        env = [line for line in env if line != ""]
        
        assert env.index("User_sophomorixSchoolname=default-school") != -1
        assert env.index("User_sophomorxCustomMulti1=test1") != -1
        assert env.index("test2") != -1
        assert env.index("User_sophomorxCustomMulti1=test1") == env.index("test2") -1
        assert env.index("Computer_sophomorixSchoolname=default-school") != -1
        assert env.index("Network_domain=linuxmuster.lan") != -1

        if script.startswith("/tmp/hooks"):
            # enshure execution order
            with open(f"{script}-date", "r") as file:
                date = int(file.read())
            assert date > lastExecutionTimestamp
            lastExecutionTimestamp = date

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

@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.config.network")
@mock.patch("linuxmusterLinuxclient7.hooks.user.readAttributes")
@mock.patch("linuxmusterLinuxclient7.hooks.computer.readAttributes")
@mock.patch("linuxmusterLinuxclient7.hooks.shares.getLocalSysvolPath")
@mock.patch("linuxmusterLinuxclient7.hooks.constants.etcBaseDir", "/tmp/hooks")
def test_runHookError(mockSharesGetLocalSysvolPath, mockComputerAttributes, mockUserAttributes, mockConfigNetwork, mockSubprocessCall):
    mockConfigNetwork.return_value = (False, None)
    mockUserAttributes.return_value = (False, None)
    mockComputerAttributes.return_value = (False, None)
    mockSharesGetLocalSysvolPath.return_value = (False, None)

    # mock ennvironment
    hooks.runRemoteHook(hooks.Type.Boot)
    mockConfigNetwork.return_value = (True, {"domain": "linuxmuster.lan"})
    hooks.runRemoteHook(hooks.Type.Boot)
    hooks.runRemoteHook(hooks.Type.Login)

    mockUserAttributes.return_value = (True, {})
    hooks.runRemoteHook(hooks.Type.Login)
    mockUserAttributes.return_value = (True, {"sophomorixSchoolname": "default-school"})
    hooks.runRemoteHook(hooks.Type.Login)

    mockComputerAttributes.return_value = (True, {})
    hooks.runRemoteHook(hooks.Type.Boot)
    mockComputerAttributes.return_value = (True, {"sophomorixSchoolname": "default-school"})
    hooks.runRemoteHook(hooks.Type.Boot)
    mockSharesGetLocalSysvolPath.return_value = (True, "/tmp/sysvol")

    createdScripts = _createRemoteHookScripts(hooks.Type.Login)

    # Scripts don't exist
    hooks.runHook(hooks.Type.Boot)
    calls = _getFirstArgugemtOfAllCalls(mockSubprocessCall)
    
    for call in calls:
        assert not call.startswith("/tmp/sysvol")

    # Scripts are not executable
    for script in createdScripts:
        os.chmod(script, 0o666)

    hooks.runHook(hooks.Type.Login)
    calls = _getFirstArgugemtOfAllCalls(mockSubprocessCall)
    
    for call in calls:
        assert not call.startswith("/tmp/sysvol")

    fileHelper.deleteDirectory("/tmp/sysvol")

# --------------------
# - Helper functions -
# --------------------

def _getFirstArgugemtOfAllCalls(mockSubprocessCall):
    calls = []
    for i in range(len(mockSubprocessCall.call_args_list)):
        firstArg = mockSubprocessCall.call_args_list[i].args[0][0]
        if not firstArg in calls:
            calls.append(firstArg)

    return calls

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
    for i in range(10):
        thisFile = f"{basedir}/on{hook.name}.d/script-{i}"
        with open(thisFile, "w") as file:
            file.write(f"#!/bin/bash\necho \"test-{i}\"\necho \"$(env)\" > {thisFile}-env\necho \"$(date +%s%N)\" > {thisFile}-date")
        os.chmod(thisFile, 0o777)
        createdFiles.append(thisFile)

    return createdFiles

def _createRemoteHookScripts(hook, sysvolPath="/tmp/sysvol", domain="linuxmuster.lan", school="default-school"):
    if not hook in hooks.remoteScriptNames:
        return []

    hookScriptPathTemplate = f"{sysvolPath}/{domain}/scripts/{school}/{{}}/linux/{hooks.remoteScriptNames[hook]}"

    createdFiles = []
    for hookKind in ["lmn", "custom"]:
        hookScriptPath = hookScriptPathTemplate.format(hookKind)
        hookDir = os.path.dirname(hookScriptPath)
        Path(hookDir).mkdir(parents=True, exist_ok=True)

        with open(hookScriptPath, "w") as file:
            file.write(f"#!/bin/bash\necho \"test-{hookKind}\"\necho \"$(env)\" > {hookScriptPath}-env")
        os.chmod(hookScriptPath, 0o777)
        createdFiles.append(hookScriptPath)

    return createdFiles