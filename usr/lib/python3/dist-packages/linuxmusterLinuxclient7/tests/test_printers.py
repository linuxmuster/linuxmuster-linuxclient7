from pathlib import Path
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

    printers.installPrinter("ipp://linuxmuster.lan/printers/printer1")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1] == ["timeout", "10", "lpadmin", "-p", "printer1", "-E", "-v", "ipp://linuxmuster.lan/printers/printer1", "-m", "everywhere", "-u", "allow:user1"]

    printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer2")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1] == ["timeout", "10", "lpadmin", "-p", "printer2", "-E", "-v", "ipp://linuxmuster.lan/printers/printer1", "-m", "everywhere", "-u", "allow:user1"]
    
    printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer2", "user2")
    assert _getCallsTo(mockSubprocessCall, "timeout")[-1] == ["timeout", "10", "lpadmin", "-p", "printer2", "-E", "-v", "ipp://linuxmuster.lan/printers/printer1", "-m", "everywhere", "-u", "allow:user2"]

    mockUserIsRoot.return_value = False
    printers.installPrinter("ipp://linuxmuster.lan/printers/printer1")
    assert _getCallsTo(mockSubprocessCall, "sudo")[-1] == ['sudo', '/usr/share/linuxmuster-linuxclient7/scripts/sudoTools', 'install-printer', '--path', 'ipp://linuxmuster.lan/printers/printer1', '--name', 'printer1']

    printers.installPrinter("ipp://linuxmuster.lan/printers/printer1", "printer2")
    assert _getCallsTo(mockSubprocessCall, "sudo")[-1] == ['sudo', '/usr/share/linuxmuster-linuxclient7/scripts/sudoTools', 'install-printer', '--path', 'ipp://linuxmuster.lan/printers/printer1', '--name', 'printer2']

# --------------------
# - Helper functions -
# --------------------

def _getCallsTo(mockSubprocessCall, program):
    calls = []
    for call_args in mockSubprocessCall.call_args_list:
        args = call_args.args[0]
        print(args)
        if args[0] == program:
            calls.append(args)
    return calls