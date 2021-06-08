import logging, os, traceback, re, sys, subprocess
from enum import Enum
from linuxmusterLinuxclient7 import user

class Level(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

def debug(message):
    _log(Level.DEBUG, message)

def info(message):
    _log(Level.INFO, message)

def warning(message):
    _log(Level.WARNING, message)

def error(message):
    _log(Level.ERROR, message)

def fatal(message):
    _log(Level.FATAL, message)

def exception(exception):
    error("=== An exception occurred ===")
    error(str(exception))
    # Only use for debugging! This will cause ugly error dialogs in X11
    #traceback.print_tb(exception.__traceback__)
    error("=== end exception ===")

def printLogs(compact=False):
    print("===========================================")
    print("=== Linuxmuster-linuxclient7 logs begin ===")

    with open("/var/log/syslog") as logfile:
        startPattern = re.compile("^.*linuxmuster-linuxclient7[^>]+======$")
        endPattern = re.compile("^.*linuxmuster-linuxclient7.*======>.*$")

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