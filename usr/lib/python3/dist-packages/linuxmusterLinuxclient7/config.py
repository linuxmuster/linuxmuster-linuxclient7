import configparser, os, yaml
from linuxmusterLinuxclient7 import logging, constants, fileHelper

def network():
    """
    Get the network configuration in `/etc/linuxmuster-linuxclient7/network.conf`

    :return: Tuple (success, dict of keys)
    :rtype: tuple
    """
    config = _readConfig()
    if config is None or not "network" in config:
        return False, None

    networkConfig = config["network"]
    if not _validateNetworkConfig(networkConfig):
        logging.error("Error when reading network.conf")
        return False, None

    return True, networkConfig

def writeNetworkConfig(newNetworkConfig):
    """
    Write the network configuration in `/etc/linuxmuster-linuxclient7/config.yml`.
    Preserves other configurations.

    :param newNetworkConfig: The new config
    :type newNetworkConfig: dict
    :return: True or False
    :rtype: bool
    """
    if not _validateNetworkConfig(newNetworkConfig):
        return False

    config = _readConfig()
    if config is None:
        config = {}
    config["network"] = newNetworkConfig

    return _writeConfig(config)

def upgrade():
    """
    Upgrade the format of the network configuration in `/etc/linuxmuster-linuxclient7/network.conf`
    This is done automatically on package upgrades.

    :return: True or False
    :rtype: bool
    """
    return _upgrade()

def delete():
    """
    Delete the network configuration file.

    :return: True or False
    :rtype: bool
    """
    legacyNetworkConfigFleDeleted = fileHelper.deleteFile(constants.legacyNetworkConfigFilePath)
    configFileDeleted = fileHelper.deleteFile(constants.configFilePath)
    return legacyNetworkConfigFleDeleted and configFileDeleted


# --------------------
# - Helper functions -
# --------------------

def _readConfig():
    if not os.path.exists(constants.configFilePath):
        networkConfig = _readLegacyNetworkConfig()
        return {"network": networkConfig} if networkConfig is not None else None

    try:
        with open(constants.configFilePath, "r") as configFile:
            yamlContent = configFile.read()
        config = yaml.safe_load(yamlContent)
        return config
    except Exception as e:
        logging.error("Error when reading config.yml")
        logging.exception(e)
        return None

def _readLegacyNetworkConfig():
    configParser = configparser.ConfigParser()
    configParser.read(constants.legacyNetworkConfigFilePath)
    try:
        rawNetworkConfig = configParser["network"]
        networkConfig = {
            "serverHostname": rawNetworkConfig["serverHostname"],
            "domain": rawNetworkConfig["domain"],
            "realm": rawNetworkConfig["realm"]
        }
        return networkConfig
    except KeyError as e:
        logging.error("Error when reading network.conf (1)")
        logging.exception(e)
        return None

def _writeConfig(config):
    try:
        with open(constants.configFilePath, "w") as configFile:
            yamlContent = yaml.dump(config)
            configFile.write(yamlContent)
        return True
    except Exception as e:
        logging.error("Error when writing config.yml")
        logging.exception(e)
        return False

def _validateNetworkConfig(networkConfig):
    requiredKeys = {"serverHostname", "domain", "realm"}
    return networkConfig is not None and networkConfig.keys() >= requiredKeys

def _upgrade():
    logging.info("Upgrading config.")
    if os.path.exists(constants.configFilePath):
        logging.info("No need to upgrade, already up-to-date.")
        return True

    logging.info("Upgrading config from network.conf to config.yml")

    config = _readConfig()
    if config is None or not "network" in config or not _validateNetworkConfig(config["network"]):
        logging.error("Error when upgrading config, network.conf is invalid")
        return False
    
    if not _writeConfig(config):
        logging.error("Error when upgrading config, could not write config.yml")
        return False
    
    fileHelper.deleteFile(constants.legacyNetworkConfigFilePath)
    logging.info("Config upgrade successfull")
    return True