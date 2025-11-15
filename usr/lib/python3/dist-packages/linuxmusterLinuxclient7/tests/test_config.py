import os, yaml
from unittest import mock
from .. import config

MOCK_FILE_PATH = f"{os.path.dirname(os.path.realpath(__file__))}/files/config"

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"{MOCK_FILE_PATH}/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/does/not/exist/config.yml")
def test_network_legacy():
    rc, networkConfig = config.network()
    assert rc
    assert networkConfig["serverHostname"] == "server.linuxmuster.legacy"
    assert networkConfig["domain"] == "linuxmuster.legacy"
    assert networkConfig["realm"] == "LINUXMUSTER.LEGACY"

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/config.yml")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{MOCK_FILE_PATH}/config.yml")
def test_network():
    rc, networkConfig = config.network()
    assert rc
    assert networkConfig["serverHostname"] == "server.linuxmuster.lan"
    assert networkConfig["domain"] == "linuxmuster.lan"
    assert networkConfig["realm"] == "LINUXMUSTER.LAN"

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"{MOCK_FILE_PATH}/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{MOCK_FILE_PATH}/config.yml")
def test_network_both():
    rc, networkConfig = config.network()
    assert rc
    assert networkConfig["serverHostname"] == "server.linuxmuster.lan"
    assert networkConfig["domain"] == "linuxmuster.lan"
    assert networkConfig["realm"] == "LINUXMUSTER.LAN"


@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/does/not/exist/config.yml")
def test_network_none():
    rc, networkConfig = config.network()
    assert not rc
    assert networkConfig is None

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{MOCK_FILE_PATH}/config.invalid-network.yml")
def test_network_invalid():
    rc, networkConfig = config.network()
    assert not rc
    assert networkConfig is None

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{MOCK_FILE_PATH}/config.yml")
def test_shares():
    sharesConfig = config.shares()
    assert "nameTemplate" in sharesConfig
    assert sharesConfig["nameTemplate"] == "{label}_{letter}"

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/does/not/exist/config.yml")
def test_shares_none():
    sharesConfig = config.shares()
    assert "nameTemplate" in sharesConfig
    assert sharesConfig["nameTemplate"] == config.constants.defaultShareNameTemplate

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{MOCK_FILE_PATH}/config.no-shares.yml")
def test_shares_missing():
    sharesConfig = config.shares()
    assert "nameTemplate" in sharesConfig
    assert sharesConfig["nameTemplate"] == config.constants.defaultShareNameTemplate

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{MOCK_FILE_PATH}/config.invalid-syntax.yml")
def test_syntax_invalid():
    rc, networkConfig = config.network()
    assert not rc
    assert networkConfig is None

@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/tmp/config.yml")
def test_writeNetworkConfig():
    _deleteFile("/tmp/config.yml")
    _copyFile(f"{MOCK_FILE_PATH}/config.yml", "/tmp/config.yml")

    newNetworkConfig = {
        "serverHostname": "server.linuxmuster.new",
        "domain": "linuxmuster.new",
        "realm": "LINUXMUSTER.NEW"
    }
    assert config.writeNetworkConfig(newNetworkConfig)

    rc, networkConfig = config.network()
    assert rc
    assert networkConfig["serverHostname"] == "server.linuxmuster.new"
    assert networkConfig["domain"] == "linuxmuster.new"
    assert networkConfig["realm"] == "LINUXMUSTER.NEW"
    assert config.shares() == {"nameTemplate": "{label}_{letter}"}


@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/tmp/config.yml")
def test_writeNetworkConfig_invalid():
    _deleteFile("/tmp/config.yml")
    _copyFile(f"{MOCK_FILE_PATH}/config.yml", "/tmp/config.yml")

    newNetworkConfig = {
        "sserverHostname": "server.linuxmuster.new",
        "domain": "linuxmuster.new",
        "realm": "LINUXMUSTER.NEW"
    }
    assert not config.writeNetworkConfig(newNetworkConfig)

    rc, networkConfig = config.network()
    assert rc
    assert networkConfig["serverHostname"] == "server.linuxmuster.lan"
    assert networkConfig["domain"] == "linuxmuster.lan"
    assert networkConfig["realm"] == "LINUXMUSTER.LAN"

@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/does/not/exist/config.yml")
def test_writeNetworkConfig_invalidPath():
    
    newNetworkConfig = {
        "serverHostname": "server.linuxmuster.new",
        "domain": "linuxmuster.new",
        "realm": "LINUXMUSTER.NEW"
    }
    assert not config.writeNetworkConfig(newNetworkConfig)

@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/tmp/config.yml")
def test_writeNetworkConfig_empty():
    _deleteFile("/tmp/config.yml")
    
    newNetworkConfig = {
        "serverHostname": "server.linuxmuster.new",
        "domain": "linuxmuster.new",
        "realm": "LINUXMUSTER.NEW"
    }
    assert config.writeNetworkConfig(newNetworkConfig)

    rc, networkConfig = config.network()
    assert rc
    assert networkConfig["serverHostname"] == "server.linuxmuster.new"
    assert networkConfig["domain"] == "linuxmuster.new"
    assert networkConfig["realm"] == "LINUXMUSTER.NEW"

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/tmp/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/tmp/config.yml")
def test_upgrade():
    _deleteFile("/tmp/config.yml")
    _deleteFile("/tmp/network.conf")
    _copyFile(f"{MOCK_FILE_PATH}/network.conf", "/tmp/network.conf")

    assert config.upgrade()
    assert not os.path.exists("/tmp/network.conf")
    assert os.path.exists("/tmp/config.yml")

    with open("/tmp/config.yml", "r") as f:
        content = f.read()
        print(content)
    yamlContent = yaml.safe_load(content)
    assert "network" in yamlContent
    assert yamlContent["network"]["serverHostname"] == "server.linuxmuster.legacy"
    assert yamlContent["network"]["domain"] == "linuxmuster.legacy"
    assert yamlContent["network"]["realm"] == "LINUXMUSTER.LEGACY"


@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"{MOCK_FILE_PATH}/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{MOCK_FILE_PATH}/config.yml")
def test_upgrade_alreadyUpToDate():
    assert config.upgrade()

    with open(config.constants.configFilePath, "r") as f:
        content = f.read()
        print(content)
    yamlContent = yaml.safe_load(content)
    assert "network" in yamlContent
    assert yamlContent["network"]["serverHostname"] == "server.linuxmuster.lan"
    assert yamlContent["network"]["domain"] == "linuxmuster.lan"
    assert yamlContent["network"]["realm"] == "LINUXMUSTER.LAN"

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"{MOCK_FILE_PATH}/network.invalid.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/tmp/config.yml")
def test_upgrade_invalid():
    _deleteFile("/tmp/config.yml")

    assert not config.upgrade()
    assert os.path.exists(f"{MOCK_FILE_PATH}/network.invalid.conf")
    assert not os.path.exists("/tmp/config.yml")

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"{MOCK_FILE_PATH}/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/does/not/exist/config.yml")
def test_upgrade_unwritable():
    assert not config.upgrade()
    assert os.path.exists(f"{MOCK_FILE_PATH}/network.invalid.conf")
    assert not os.path.exists("/tmp/config.yml")

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/does/not/exist/config.yml")
def test_upgrade_nonexistent():
    assert not config.upgrade()

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/tmp/config.yml")
def test_deleteNetworkConfig():
    _deleteFile("/tmp/network.conf")
    _deleteFile("/tmp/config.yml")

    _copyFile(f"{MOCK_FILE_PATH}/config.yml", "/tmp/config.yml")

    assert config.deleteNetworkConfig()
    assert os.path.exists("/tmp/config.yml")
    assert config.network() == (False, None)
    assert config.shares() == {"nameTemplate": "{label}_{letter}"}

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/does/not/exist/config.yml")
def test_deleteNetworkConfig_nonexistent():
    assert config.deleteNetworkConfig()

# --------------------
# - Helper functions -
# --------------------

def _deleteFile(path):
    if os.path.exists(path):
        os.remove(path)

def _copyFile(src, dst):
    with open(src, "r") as fsrc:
        with open(dst, "w") as fdst:
            fdst.write(fsrc.read())