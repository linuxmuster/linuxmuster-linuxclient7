import configparser, re
from linuxmusterLinuxclient7 import logging, constants

def network():
    """
    Get the network configuration in `/etc/linuxmusterLinuxclient7/network.conf`

    :return: Tuple (success, dict of keys)
    :rtype: tuple
    """
    rc, rawNetworkConfig = _readNetworkConfig()
    if not rc:
        return False, None

    if not _checkNetworkConfigVersion(rawNetworkConfig)[0]:
        return False, None

    networkConfig = {}

    try:
        networkConfig["serverHostname"] = rawNetworkConfig["serverHostname"]
        networkConfig["domain"] = rawNetworkConfig["domain"]
        networkConfig["realm"] = rawNetworkConfig["realm"]
    except KeyError as e:
        logging.error("Error when reading network.conf (2)")
        logging.exception(e)
        return False, None

    return True, networkConfig

def writeNetworkConfig(newNetworkConfig):
    """
    Write the network configuration in `/etc/linuxmusterLinuxclient7/network.conf`

    :param newNetworkConfig: The new config
    :type newNetworkConfig: dict
    :return: True or False
    :rtype: bool
    """
    networkConfig = configparser.ConfigParser(interpolation=None)

    try:
        networkConfig["network"] = {}
        networkConfig["network"]["version"] = str(_networkConfigVersion())
        networkConfig["network"]["serverHostname"] = newNetworkConfig["serverHostname"]
        networkConfig["network"]["domain"] = newNetworkConfig["domain"]
        networkConfig["network"]["realm"] = newNetworkConfig["realm"]
    except Exception as e:
        logging.error("Error when preprocessing new network configuration!")
        logging.exception(e)
        return False

    try:
        logging.info("Writing new network Configuration")
        with open(constants.networkConfigFilePath, 'w') as networkConfigFile:
            networkConfig.write(networkConfigFile)

    except Exception as e:
        logging.error("Failed!")
        logging.exception(e)
        return False

    return True

def upgrade():
    """
    Upgrade the format of the network configuration in `/etc/linuxmusterLinuxclient7/network.conf`
    This is done automatically on package upgrades.

    :return: True or False
    :rtype: bool
    """
    return _upgradeNetworkConfig()

# --------------------
# - Helper functions -
# --------------------

def _readNetworkConfig():
    configParser = configparser.ConfigParser()
    configParser.read(constants.networkConfigFilePath)
    try:
        rawNetworkConfig = configParser["network"]
        return True, rawNetworkConfig
    except KeyError as e:
        logging.error("Error when reading network.conf (1)")
        logging.exception(e)
        return False, None
    return configParser

def _networkConfigVersion():
    return 1

def _checkNetworkConfigVersion(rawNetworkConfig):
    try:
        networkConfigVersion = int(rawNetworkConfig["version"])
    except KeyError as e:
        logging.warning("The network.conf version could not be identified, assuming 0")
        networkConfigVersion = 0

    if networkConfigVersion != _networkConfigVersion():
        logging.warning("The network.conf Version is a mismatch!")
        return False, networkConfigVersion

    return True, networkConfigVersion

def _upgradeNetworkConfig():
    logging.info("Upgrading network config.")
    rc, rawNetworkConfig = _readNetworkConfig()
    if not rc:
        return False

    rc, networkConfigVersion = _checkNetworkConfigVersion(rawNetworkConfig)
    if rc:
        logging.info("No need to upgrade, already up-to-date.")
        return True

    logging.info("Upgrading network config from {0} to {1}".format(networkConfigVersion, _networkConfigVersion()))
    
    if networkConfigVersion > _networkConfigVersion():
        logging.error("Cannot upgrade from a newer version to an older one!")
        return False

    try:
        if networkConfigVersion == 0:
            newNetworkConfig = {}
            newNetworkConfig["serverHostname"] = rawNetworkConfig["serverHostname"] + "." + rawNetworkConfig["domain"]
            newNetworkConfig["domain"] = rawNetworkConfig["domain"]
            newNetworkConfig["realm"] = rawNetworkConfig["domain"].upper()
            return writeNetworkConfig(newNetworkConfig)
    except Exception as e:
        logging.error("Error when upgrading network config!")
        logging.exception(e)
        return False

    return True