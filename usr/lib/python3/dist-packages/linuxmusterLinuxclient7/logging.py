import traceback, re, sys, subprocess
from enum import Enum
from linuxmusterLinuxclient7 import config

class Level(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

def debug(message):
    """
    Do a debug log.

    :param message: The message to log
    :type message: str
    """
    _log(Level.DEBUG, message)

def info(message):
    """
    Do an info log.

    :param message: The message to log
    :type message: str
    """
    _log(Level.INFO, message)

def warning(message):
    """
    Do a warning log.

    :param message: The message to log
    :type message: str
    """
    _log(Level.WARNING, message)

def error(message):
    """
    Do an error log.

    :param message: The message to log
    :type message: str
    """
    _log(Level.ERROR, message)

def fatal(message):
    """
    Do a fatal log. If used in onLogin hook, this will create a dialog containing the message.

    :param message: The message to log
    :type message: str
    """
    _log(Level.FATAL, message)

def exception(exception):
    """
    Log an exception

    :param exception: The exception to log
    :type exception: Exception
    """
    error("=== An exception occurred ===")
    error(str(exception))
    # Only use for debugging! This will cause ugly error dialogs in X11
    #traceback.print_tb(exception.__traceback__)
    error("=== end exception ===")

def printLogs(compact=False,anonymize=False):
    """
    Print logs of linuxmuster-linuxclient7 from `/var/log/syslog`.

    :param compact: If set to True, some stuff like time and date will be removed. Defaults to False
    :type compact: bool, optional
    :param anonymize: If set to True, domain/realm/serverHostname will be replaced by linuxmuster.lan. Defaults to False
    :type anonymize: bool, optional
    """
    print("===========================================")
    print("=== Linuxmuster-linuxclient7 logs begin ===")

    (rc, networkConfig) = config.network()
    if rc:
        domain = networkConfig["domain"]
        tld = domain.split(".")[-1]
        host = domain.split(".")[-2]
        serverHostname = networkConfig["serverHostname"]
        realm = networkConfig["realm"]

    with open("/var/log/syslog") as logfile:
        startPattern = re.compile("^.*[^>]+started ======$")
        endPattern = re.compile("^.*======>.*end ======$")

        currentlyInsideOfLinuxmusterLinuxclient7Log = False

        for line in logfile:
            line = line.replace("\n", "")
            if startPattern.fullmatch(line):
                currentlyInsideOfLinuxmusterLinuxclient7Log = True
                print("\n")

            if currentlyInsideOfLinuxmusterLinuxclient7Log:
                if compact:
                    # "^([^ ]+[ ]+){4}" matches "Apr  6 14:39:23 somehostname" 
                    line = re.sub("^([^ ]+[ ]+){4}", "", line)
                if anonymize and rc:
                    line = re.sub(serverHostname, "server.linuxmuster.lan", line)
                    line = re.sub(domain, "linuxmuster.lan", line)
                    line = re.sub(realm, "LINUXMUSTER.LAN", line)
                    line = re.sub(f"DC={host},DC={tld}", "DC=linuxmuster,DC=lan", line)

                print(line)

            if endPattern.fullmatch(line):
                currentlyInsideOfLinuxmusterLinuxclient7Log = False
                print("\n")
            
    print("=== Linuxmuster-linuxclient7 logs end ===")
    print("=========================================")

# --------------------
# - Helper functions -
# --------------------

def _log(level, message):
    #if level == Level.DEBUG:
    #    return
    if level == Level.FATAL:
        sys.stderr.write(message)
        
    print("[{0}] {1}".format(level.name, message))
    message = message.replace("'", "")
    subprocess.call(["logger", "-t", "linuxmuster-linuxclient7", f"[{level.name}] {message}"])
