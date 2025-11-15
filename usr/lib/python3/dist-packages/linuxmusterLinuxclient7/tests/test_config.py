import os, yaml
from unittest import mock
from .. import config

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"{os.path.dirname(os.path.realpath(__file__))}/files/config/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/does/not/exist/config.yml")
def test_network_legacy():
    rc, networkConfig = config.network()
    assert rc
    assert networkConfig["serverHostname"] == "server.linuxmuster.legacy"
    assert networkConfig["domain"] == "linuxmuster.legacy"
    assert networkConfig["realm"] == "LINUXMUSTER.LEGACY"

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/config.yml")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{os.path.dirname(os.path.realpath(__file__))}/files/config/config.yml")
def test_network():
    rc, networkConfig = config.network()
    assert rc
    assert networkConfig["serverHostname"] == "server.linuxmuster.lan"
    assert networkConfig["domain"] == "linuxmuster.lan"
    assert networkConfig["realm"] == "LINUXMUSTER.LAN"

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"{os.path.dirname(os.path.realpath(__file__))}/files/config/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{os.path.dirname(os.path.realpath(__file__))}/files/config/config.yml")
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
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{os.path.dirname(os.path.realpath(__file__))}/files/config/config.invalid-network.yml")
def test_network_invalid():
    rc, networkConfig = config.network()
    assert not rc
    assert networkConfig is None

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{os.path.dirname(os.path.realpath(__file__))}/files/config/config.invalid-syntax.yml")
def test_syntax_invalid():
    rc, networkConfig = config.network()
    assert not rc
    assert networkConfig is None

@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/tmp/config.yml")
def test_writeNetworkConfig():
    if os.path.exists("/tmp/config.yml"):
        os.remove("/tmp/config.yml")

    with open(f"{os.path.dirname(os.path.realpath(__file__))}/files/config/config.yml", "r") as fsrc:
        with open("/tmp/config.yml", "w") as fdst:
            fdst.write(fsrc.read())

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

    # TODO: once there are more config options, test that they are preserved

@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/tmp/config.yml")
def test_writeNetworkConfig_invalid():
    if os.path.exists("/tmp/config.yml"):
        os.remove("/tmp/config.yml")

    with open(f"{os.path.dirname(os.path.realpath(__file__))}/files/config/config.yml", "r") as fsrc:
        with open("/tmp/config.yml", "w") as fdst:
            fdst.write(fsrc.read())

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
    if os.path.exists("/tmp/config.yml"):
        os.remove("/tmp/config.yml")
    
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
    if os.path.exists("/tmp/config.yml"):
        os.remove("/tmp/config.yml")

    if os.path.exists("/tmp/network.conf"):
        os.remove("/tmp/network.conf")

    with open(f"{os.path.dirname(os.path.realpath(__file__))}/files/config/network.conf", "r") as fsrc:
        with open("/tmp/network.conf", "w") as fdst:
            fdst.write(fsrc.read())

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


@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"{os.path.dirname(os.path.realpath(__file__))}/files/config/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"{os.path.dirname(os.path.realpath(__file__))}/files/config/config.yml")
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

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"{os.path.dirname(os.path.realpath(__file__))}/files/config/network.invalid.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/tmp/config.yml")
def test_upgrade_invalid():
    if os.path.exists("/tmp/config.yml"):
        os.remove("/tmp/config.yml")

    assert not config.upgrade()
    assert os.path.exists(f"{os.path.dirname(os.path.realpath(__file__))}/files/config/network.invalid.conf")
    assert not os.path.exists("/tmp/config.yml")

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/does/not/exist/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/does/not/exist/config.yml")
def test_upgrade_nonexistent():
    assert not config.upgrade()

@mock.patch("linuxmusterLinuxclient7.config.constants.legacyNetworkConfigFilePath", f"/tmp/network.conf")
@mock.patch("linuxmusterLinuxclient7.config.constants.configFilePath", f"/tmp/config.yml")
def test_delete():
    if os.path.exists("/tmp/network.conf"):
        os.remove("/tmp/network.conf")
    if os.path.exists("/tmp/config.yml"):
        os.remove("/tmp/config.yml")

    with open(f"{os.path.dirname(os.path.realpath(__file__))}/files/config/network.conf", "r") as fsrc:
        with open("/tmp/network.conf", "w") as fdst:
            fdst.write(fsrc.read())
    with open(f"{os.path.dirname(os.path.realpath(__file__))}/files/config/config.yml", "r") as fsrc:
        with open("/tmp/config.yml", "w") as fdst:
            fdst.write(fsrc.read())

    assert config.delete()
    assert not os.path.exists("/tmp/network.conf")
    assert not os.path.exists("/tmp/config.yml")