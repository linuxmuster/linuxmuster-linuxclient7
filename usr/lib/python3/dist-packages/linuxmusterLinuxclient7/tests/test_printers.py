from subprocess import CompletedProcess
from unittest import mock
from .. import printers

def test_printerNetworkPathIsValid():
    assert printers._printerNetworkPathIsValid("ipp://server/printers/P1")
    assert printers._printerNetworkPathIsValid("smb://server/P1")
    assert printers._printerNetworkPathIsValid("https://server/printers/P1")
    assert not printers._printerNetworkPathIsValid("file:///etc/passwd")
    assert not printers._printerNetworkPathIsValid("/etc/passwd")
    assert not printers._printerNetworkPathIsValid("")
    assert not printers._printerNetworkPathIsValid(None)
    assert not printers._printerNetworkPathIsValid("ipp://server/\nP1")

def test_printerNameIsValid():
    assert printers._printerNameIsValid("EW-farblaser")
    assert printers._printerNameIsValid("printer1")
    assert printers._printerNameIsValid("Drucker-Büro_1.OG")
    assert not printers._printerNameIsValid("")
    assert not printers._printerNameIsValid(None)
    assert not printers._printerNameIsValid("-flag")
    assert not printers._printerNameIsValid("a/b")
    assert not printers._printerNameIsValid("a b")
    assert not printers._printerNameIsValid("a#b")
    assert not printers._printerNameIsValid("a\nb")

@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.user.isRoot")
@mock.patch("linuxmusterLinuxclient7.hooks.user.username")
def test_installPrinterRejectsInvalidInput(mockUserUsername, mockUserIsRoot, mockSubprocessCall):
    mockUserIsRoot.return_value = True
    mockUserUsername.return_value = "user1"

    assert not printers.installPrinter("file:///etc/passwd", "printer1")
    assert not printers.installPrinter("ipp://server/printers/P1", "../evil")
    assert _getCallsTo(mockSubprocessCall, "timeout") == []

def test_translateSambaToIpp():
    assert printers.translateSambaToIpp("\\\\linuxmuster.lan\\printer1") == (True, "ipp://linuxmuster.lan/printers/printer1")
    assert printers.translateSambaToIpp("\\\\linuxmuster.lan\\") == (False, None)
    assert printers.translateSambaToIpp("\\\\linuxmuster.lan") == (False, None)
    assert printers.translateSambaToIpp("\\\\\\printer1") == (False, None)


@mock.patch("subprocess.run")
@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.user.isRoot")
@mock.patch("linuxmusterLinuxclient7.hooks.user.username")
def test_installPrinter(mockUserUsername, mockUserIsRoot, mockSubprocessCall, mockSubprocessRun):
    mockSubprocessRun.return_value = CompletedProcess(args=["lpstat", "-l", "-p", "printer1"], returncode=1)
    mockSubprocessCall.return_value = 0
    mockUserIsRoot.return_value = True
    mockUserUsername.return_value = "user1"

    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1] == ["timeout", "10", "/usr/sbin/lpadmin", "-p", "printer1", "-E", "-v", "ipp://linuxmuster.lan/printers/printer1", "-m", "everywhere", "-u", "allow:user1"]

    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer2")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1] == ["timeout", "10", "/usr/sbin/lpadmin", "-p", "printer2", "-E", "-v", "ipp://linuxmuster.lan/printers/printer1", "-m", "everywhere", "-u", "allow:user1"]
    
    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer2", "user2")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1] == ["timeout", "10", "/usr/sbin/lpadmin", "-p", "printer2", "-E", "-v", "ipp://linuxmuster.lan/printers/printer1", "-m", "everywhere", "-u", "allow:user2"]

    mockUserIsRoot.return_value = False
    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1")
    assert _getCallsTo(mockSubprocessCall, "sudo")[-1] == ['sudo', '/usr/share/linuxmuster-linuxclient7/scripts/sudoTools', 'install-printer', '--path', 'ipp://linuxmuster.lan/printers/printer1', '--name', 'printer1']

    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer2")
    assert _getCallsTo(mockSubprocessCall, "sudo")[-1] == ['sudo', '/usr/share/linuxmuster-linuxclient7/scripts/sudoTools', 'install-printer', '--path', 'ipp://linuxmuster.lan/printers/printer1', '--name', 'printer2']

@mock.patch("subprocess.run")
@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.user.isRoot")
@mock.patch("linuxmusterLinuxclient7.hooks.user.username")
def test_installPrinterError(mockUserUsername, mockUserIsRoot, mockSubprocessCall, mockSubprocessRun):
    mockSubprocessRun.return_value = CompletedProcess(args=["lpstat", "-l", "-p", "printer1"], returncode=1)
    mockSubprocessCall.return_value = 124
    mockUserIsRoot.return_value = True
    mockUserUsername.return_value = "user1"

    assert not printers.installPrinter("ipp://linuxmuster.lan/printers/printer1")

    mockSubprocessCall.return_value = 1
    assert not printers.installPrinter("ipp://linuxmuster.lan/printers/printer1")


@mock.patch("subprocess.call")
@mock.patch("subprocess.run")
def test_uninstallAllPrintersOfUser(mockSubprocessRun, mockSubprocessCall):
    mockSubprocessCall.return_value = 0
    lpstatStdout = """printer printer1 is idle.  enabled since Sat 02 Jul 2022 06:07:39 PM CEST
printer printer2 is idle.  enabled since Sat 09 Jul 2022 08:04:43 PM CEST
invalid"""
    mockSubprocessRun.return_value = CompletedProcess(args=["lpstat", "-U", "user1", "-p"], returncode=0, stdout=lpstatStdout)

    assert printers.uninstallAllPrintersOfUser("user1")
    assert ['/usr/bin/lpstat', '-U', 'user1', '-p'] in _getCallsTo(mockSubprocessRun, "/usr/bin/lpstat")
    assert _getCallsTo(mockSubprocessCall, "timeout") == [["timeout", "10", "/usr/sbin/lpadmin", "-x", "printer1"], ["timeout", "10", "/usr/sbin/lpadmin", "-x", "printer2"]]

    mockSubprocessRun.return_value = CompletedProcess(args=["lpstat", "-U", "user1", "-p"], returncode=1)
    assert printers.uninstallAllPrintersOfUser("user1")

@mock.patch("subprocess.call")
@mock.patch("subprocess.run")
def test_uninstallAllPrintersOfUserError(mockSubprocessRun, mockSubprocessCall):
    lpstatStdout = """printer printer1 is idle.  enabled since Sat 02 Jul 2022 06:07:39 PM CEST
printer printer2 is idle.  enabled since Sat 09 Jul 2022 08:04:43 PM CEST
invalid"""
    mockSubprocessRun.return_value = CompletedProcess(args=["lpstat", "-U", "user1", "-p"], returncode=0, stdout=lpstatStdout)
    mockSubprocessCall.return_value = 1
    assert not printers.uninstallAllPrintersOfUser("user1")

    mockSubprocessRun.return_value = CompletedProcess(args=["lpstat", "-U", "user1", "-p"], returncode=0, stdout=lpstatStdout)
    mockSubprocessCall.return_value = 124
    assert not printers.uninstallAllPrintersOfUser("user1")

@mock.patch("subprocess.run")
def test_getAllowedUsersOfPrinter(mockSubprocessRun):
    lpstatStdout = "printer printer1 is idle.\n\tUsers allowed:\n\t\tuser1\n\t\tuser2\n\tForms allowed:\n\t\t(none)\n"
    mockSubprocessRun.return_value = CompletedProcess(args=["lpstat", "-l", "-p", "printer1"], returncode=0, stdout=lpstatStdout)
    assert printers._getAllowedUsersOfPrinter("printer1") == ["user1", "user2"]
    assert mockSubprocessRun.call_args.kwargs["env"]["LC_ALL"] == "C"

    lpstatStdout = "printer printer1 is idle.\n\tUsers allowed:\n\t\t(all)\n\tForms allowed:\n\t\t(none)\n"
    mockSubprocessRun.return_value = CompletedProcess(args=["lpstat", "-l", "-p", "printer1"], returncode=0, stdout=lpstatStdout)
    assert printers._getAllowedUsersOfPrinter("printer1") == []

    mockSubprocessRun.return_value = CompletedProcess(args=["lpstat", "-l", "-p", "printer1"], returncode=1, stdout="")
    assert printers._getAllowedUsersOfPrinter("printer1") == []

@mock.patch("subprocess.run")
@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.user.isRoot")
def test_installPrinterKeepsAllowedUsers(mockUserIsRoot, mockSubprocessCall, mockSubprocessRun):
    mockUserIsRoot.return_value = True
    mockSubprocessCall.return_value = 0
    lpstatStdout = "printer printer1 is idle.\n\tUsers allowed:\n\t\tuser1\n\tForms allowed:\n\t\t(none)\n"
    mockSubprocessRun.return_value = CompletedProcess(args=["lpstat", "-l", "-p", "printer1"], returncode=0, stdout=lpstatStdout)

    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer1", "user2")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1][-2:] == ["-u", "allow:user1,user2"]

    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer1", "user1")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1][-2:] == ["-u", "allow:user1"]

@mock.patch("subprocess.call")
@mock.patch("subprocess.run")
def test_uninstallAllPrintersOfUserKeepsPrinterForOtherUsers(mockSubprocessRun, mockSubprocessCall):
    mockSubprocessCall.return_value = 0
    lpstatPrinters = CompletedProcess(args=["lpstat", "-U", "user1", "-p"], returncode=0, stdout="printer printer1 is idle.  enabled since Sat 02 Jul 2022 06:07:39 PM CEST")
    lpstatAllowedUsers = CompletedProcess(args=["lpstat", "-l", "-p", "printer1"], returncode=0, stdout="printer printer1 is idle.\n\tUsers allowed:\n\t\tuser1\n\t\tuser2\n\tForms allowed:\n\t\t(none)\n")
    mockSubprocessRun.side_effect = [lpstatPrinters, lpstatAllowedUsers]

    assert printers.uninstallAllPrintersOfUser("user1")
    assert _getCallsTo(mockSubprocessCall, "timeout") == [["timeout", "10", "/usr/sbin/lpadmin", "-p", "printer1", "-u", "allow:user2"]]

    mockSubprocessCall.return_value = 1
    mockSubprocessRun.side_effect = [lpstatPrinters, lpstatAllowedUsers]
    assert not printers.uninstallAllPrintersOfUser("user1")

# --------------------
# - Helper functions -
# --------------------

def _getCallsTo(mockSubprocessCall, program):
    calls = []
    for call_args in mockSubprocessCall.call_args_list:
        args = call_args.args[0]
        print(args)
        if (type(args) == list and args[0] == program) or (type(args) == str and args.startswith(f"{program} ")):
            calls.append(args)
    return calls