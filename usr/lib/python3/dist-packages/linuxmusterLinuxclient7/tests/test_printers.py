from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock
from .. import printers
import pytest, os

def test_translateSambaToIpp():
    assert printers.translateSambaToIpp("\\\\linuxmuster.lan\\printer1") == (True, "ipp://linuxmuster.lan/printers/printer1")
    assert printers.translateSambaToIpp("\\\\linuxmuster.lan\\") == (False, None)
    assert printers.translateSambaToIpp("\\\\linuxmuster.lan") == (False, None)
    assert printers.translateSambaToIpp("\\\\\\printer1") == (False, None)


@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.user.isRoot")
@mock.patch("linuxmusterLinuxclient7.hooks.user.username")
def test_installPrinter(mockUserUsername, mockUserIsRoot, mockSubprocessCall):
    mockSubprocessCall.return_value = 0
    mockUserIsRoot.return_value = True
    mockUserUsername.return_value = "user1"

    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1] == ["timeout", "10", "lpadmin", "-p", "printer1", "-E", "-v", "ipp://linuxmuster.lan/printers/printer1", "-m", "everywhere", "-u", "allow:user1"]

    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer2")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1] == ["timeout", "10", "lpadmin", "-p", "printer2", "-E", "-v", "ipp://linuxmuster.lan/printers/printer1", "-m", "everywhere", "-u", "allow:user1"]
    
    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer2", "user2")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1] == ["timeout", "10", "lpadmin", "-p", "printer2", "-E", "-v", "ipp://linuxmuster.lan/printers/printer1", "-m", "everywhere", "-u", "allow:user2"]

    mockUserIsRoot.return_value = False
    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1")
    assert _getCallsTo(mockSubprocessCall, "sudo")[-1] == ['sudo', '/usr/share/linuxmuster-linuxclient7/scripts/sudoTools', 'install-printer', '--path', 'ipp://linuxmuster.lan/printers/printer1', '--name', 'printer1']

    assert printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer2")
    assert _getCallsTo(mockSubprocessCall, "sudo")[-1] == ['sudo', '/usr/share/linuxmuster-linuxclient7/scripts/sudoTools', 'install-printer', '--path', 'ipp://linuxmuster.lan/printers/printer1', '--name', 'printer2']

@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.hooks.user.isRoot")
@mock.patch("linuxmusterLinuxclient7.hooks.user.username")
def test_installPrinterError(mockUserUsername, mockUserIsRoot, mockSubprocessCall):
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
    assert _getCallsTo(mockSubprocessRun, "lpstat")[-1] == "lpstat -U user1 -p"
    assert _getCallsTo(mockSubprocessCall, "timeout") == [["timeout", "10", "lpadmin", "-x", "printer1"], ["timeout", "10", "lpadmin", "-x", "printer2"]]

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