from subprocess import CompletedProcess
from unittest import mock
from .. import realm
import os

@mock.patch("subprocess.call")
def test_join(mockSubprocessCall):
    mockSubprocessCall.return_value = 0
    assert realm.join("linuxmuster.lan", "global-admin")
    calls = _getCallsTo(mockSubprocessCall, "realm")
    assert len(calls) == 1
    assert ["realm", "join", "-v", "linuxmuster.lan", "-U", "global-admin"] in calls

    mockSubprocessCall.return_value = 1
    assert not realm.join("linuxmuster.lan", "global-admin")

@mock.patch("subprocess.call")
def test_leave(mockSubprocessCall):
    mockSubprocessCall.return_value = 0

    assert realm.leave("linuxmuster.lan")
    calls = _getCallsTo(mockSubprocessCall, "realm")
    assert len(calls) == 1
    assert ["realm", "leave", "linuxmuster.lan"] in calls

    mockSubprocessCall.return_value = 1
    assert not realm.leave("linuxmuster.lan")

@mock.patch("subprocess.run")
def test_getJoinedDomains(mockSubprocessRun):
    realmListStdout = """linuxmuster.lan
windowsmuster.lan"""
    mockSubprocessRun.return_value = CompletedProcess(args=["realm", "list", "--name-only"], returncode=0, stdout=realmListStdout)

    assert realm.getJoinedDomains() == (True, ["linuxmuster.lan", "windowsmuster.lan"])
    calls = _getCallsTo(mockSubprocessRun, "realm")
    assert len(calls) == 1
    assert "realm list --name-only" in calls

    mockSubprocessRun.return_value = CompletedProcess(args=["realm", "list", "--name-only"], returncode=1, stdout="")
    assert realm.getJoinedDomains() == (False, None)

@mock.patch("linuxmusterLinuxclient7.realm.leave")
@mock.patch("linuxmusterLinuxclient7.realm.getJoinedDomains")
def test_leaveAll(mockGetJoinedDomains, mockLeave):
    mockGetJoinedDomains.return_value = (True, ["linuxmuster.lan", "windowsmuster.lan"])
    mockLeave.return_value = True
    assert realm.leaveAll()
    calls = _getCalls(mockLeave)
    assert len(calls) == 2
    assert "linuxmuster.lan" in calls
    assert "windowsmuster.lan" in calls

    mockLeave.return_value = False
    assert not realm.leaveAll()

    mockLeave.return_value = True
    mockGetJoinedDomains.return_value = (False, None)
    assert not realm.leaveAll()


@mock.patch("linuxmusterLinuxclient7.realm.getJoinedDomains")
def test_isJoined(mockGetJoinedDomains):
    mockGetJoinedDomains.return_value = (True, ["linuxmuster.lan", "windowsmuster.lan"])
    assert realm.isJoined()
    mockGetJoinedDomains.return_value = (False, None)
    assert not realm.isJoined()
    mockGetJoinedDomains.return_value = (True, ["linuxmuster.lan"])
    assert realm.isJoined()

@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.computer.krbHostName", lambda : "linuxmuster.lan")
def test_pullKerberosTicketForComputerAccount(mockSubprocessCall):
    mockSubprocessCall.return_value = 0
    assert realm.pullKerberosTicketForComputerAccount()
    calls = _getCallsTo(mockSubprocessCall, "kinit")
    assert len(calls) == 1
    assert ["kinit", "-k", "linuxmuster.lan"] in calls

    mockSubprocessCall.return_value = 1
    assert not realm.pullKerberosTicketForComputerAccount()

@mock.patch("subprocess.call")
@mock.patch("linuxmusterLinuxclient7.realm.isJoined")
@mock.patch("linuxmusterLinuxclient7.realm.pullKerberosTicketForComputerAccount")
def test_verifyDomainJoin(mockPullKerberosTicketForComputerAccount, mockIsJoined, mockSubprocessCall):
    mockPullKerberosTicketForComputerAccount.return_value = True
    mockIsJoined.return_value = True
    mockSubprocessCall.return_value = 0

    assert realm.verifyDomainJoin()
    calls = _getCallsTo(mockSubprocessCall, "getent")
    assert len(calls) == 1
    assert ["getent", "group", "domain users"] in calls

    mockIsJoined.return_value = False
    assert not realm.verifyDomainJoin()

    mockIsJoined.return_value = True
    mockSubprocessCall.return_value = 1
    assert not realm.verifyDomainJoin()

    mockSubprocessCall.return_value = 0
    mockPullKerberosTicketForComputerAccount.return_value = False
    assert not realm.verifyDomainJoin()

@mock.patch("subprocess.run")
def test_discoverDomains(mockSubprocessRun):
    realmListStdout = """linuxmuster.lan
windowsmuster.lan"""
    mockSubprocessRun.return_value = CompletedProcess(args=["realm", "discover", "--name-only"], returncode=0, stdout=realmListStdout)
    assert realm.discoverDomains() == (True, ["linuxmuster.lan", "windowsmuster.lan"])
    calls = _getCallsTo(mockSubprocessRun, "realm")
    assert ['realm', 'discover', '--name-only'] == calls[-1]

    mockSubprocessRun.return_value = CompletedProcess(args=["realm", "discover", "--name-only"], returncode=1, stdout="")
    assert realm.discoverDomains() == (False, None)

    mockSubprocessRun.return_value = CompletedProcess(args=["realm", "discover", "--name-only"], returncode=0, stdout="linuxmuster.lan")
    assert realm.discoverDomains("linuxmuster.lan") == (True, ["linuxmuster.lan"])
    calls = _getCallsTo(mockSubprocessRun, "realm")
    assert len(calls) == 3
    assert ['realm', 'discover', '--name-only', "linuxmuster.lan"] == calls[-1]

@mock.patch("subprocess.run")
def test_getDomainConfig(mockSubprocessRun):
    adcliInfoStdout = """[domain]
domain-name = linuxmuster.lan
domain-short = LINUXMUSTER
domain-forest = linuxmuster.lan
domain-controller = server.linuxmuster.lan
domain-controller-site = Default-First-Site-Name
domain-controller-flags = pdc gc ldap ds kdc timeserv closest writable good-timeserv full-secret
domain-controller-usable = yes
domain-controllers = server.linuxmuster.lan
[computer]
computer-site = Default-First-Site-Name"""
    mockSubprocessRun.return_value = CompletedProcess(args=["adcli", "info", "linuxmuster.lan"], returncode=0, stdout=adcliInfoStdout)

    assert realm.getDomainConfig("linuxmuster.lan") == (True, {"domain-controller": "server.linuxmuster.lan", "domain-name": "linuxmuster.lan"})
    calls = _getCallsTo(mockSubprocessRun, "adcli")
    assert len(calls) == 1
    assert "adcli info 'linuxmuster.lan'" in calls

    mockSubprocessRun.return_value = CompletedProcess(args=["adcli", "info", "linuxmuster.lan"], returncode=1, stdout="")
    assert realm.getDomainConfig("linuxmuster.lan") == (False, None)

    adcliInfoStdout = """[domain]
domain-short = LINUXMUSTER
domain-forest = linuxmuster.lan
domain-controller = server.linuxmuster.lan
domain-controller-site = Default-First-Site-Name
domain-controller-flags = pdc gc ldap ds kdc timeserv closest writable good-timeserv full-secret
domain-controller-usable = yes
domain-controllers = server.linuxmuster.lan
[computer]
computer-site = Default-First-Site-Name"""
    mockSubprocessRun.return_value = CompletedProcess(args=["adcli", "info", "linuxmuster.lan"], returncode=0, stdout=adcliInfoStdout)
    assert realm.getDomainConfig("linuxmuster.lan") == (False, None)

@mock.patch("subprocess.call")
def test_clearUserCache(mockSubprocessCall):
    mockSubprocessCall.return_value = 0
    assert realm.clearUserCache()
    calls = _getCallsTo(mockSubprocessCall, "sssctl")
    assert len(calls) == 1
    assert ["sssctl", "cache-remove", "--stop", "--start", "--override"] in calls

    mockSubprocessCall.return_value = 1
    assert not realm.clearUserCache()

# --------------------
# - Helper functions -
# --------------------

def _getCalls(mock):
    calls = []
    for call_args in mock.call_args_list:
        calls.append(call_args.args[0])
    return calls

def _getCallsTo(mockSubprocessCall, program):
    calls = []
    for call_args in mockSubprocessCall.call_args_list:
        args = call_args.args[0]
        print(args)
        if (type(args) == list and args[0] == program) or (type(args) == str and args.startswith(f"{program} ")):
            calls.append(args)
    return calls