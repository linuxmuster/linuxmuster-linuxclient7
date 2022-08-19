from unittest import mock
from .. import logging
import os

@mock.patch("subprocess.call")
def test_forAllLevels(mockSubprocessCall):
    logging.debug("debug")
    logging.info("info")
    logging.warning("warning")
    logging.error("error")
    logging.fatal("fatal")
    logging.exception(Exception("exception"))

    logs = _getLoggedLogs(mockSubprocessCall)
    assert logs == ["[DEBUG] debug", "[INFO] info", "[WARNING] warning", "[ERROR] error", "[FATAL] fatal", "[ERROR] === An exception occurred ===", "[ERROR] exception", "[ERROR] === end exception ==="]

@mock.patch("linuxmusterLinuxclient7.logging.print")
@mock.patch("linuxmusterLinuxclient7.logging.open")
@mock.patch("linuxmusterLinuxclient7.config.network")
def test_printLogs(mockConfigNetwork, mockOpen, mockPrint):
    syslogFile = f"{os.path.dirname(os.path.realpath(__file__))}/files/logging/syslog"
    mockOpen.return_value = open(syslogFile)
    mockConfigNetwork.return_value = (True, {"domain": "internal-domain.lan", "serverHostname": "server01.internal-domain.lan", "realm": "INTERNAL-DOMAIN"})

    logging.printLogs(True, True)
    lines = _getPrintedLines(mockPrint)
    text = "\n".join(lines)
    assert "[INFO] ====== onLogin started ======" in text
    assert "[INFO] ======> onLogin end ======" in text
    assert "THIS SHOULD NOT BE PRINTED" not in text
    assert "internal-domain" not in text
    assert "Aug 19 11:55:52" not in text

# --------------------
# - Helper functions -
# --------------------

def _getLoggedLogs(mockSubprocessCall):
    logs = []
    for call_args in mockSubprocessCall.call_args_list:
        args = call_args.args[0]
        print(args)
        if type(args) == list and args[0] == "logger":
            logs.append(args[3])
    return logs

def _getPrintedLines(mockPrint):
    lines = []
    for call_args in mockPrint.call_args_list:
        lines.append(call_args.args[0])
    return lines