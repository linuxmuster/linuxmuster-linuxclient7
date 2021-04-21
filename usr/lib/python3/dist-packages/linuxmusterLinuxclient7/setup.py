import os
import re
import sys
import configparser
from subprocess import PIPE, run
from linuxmusterLinuxclient7 import logging, constants, hooks, shares, config, user, templates, realm, fileHelper, printers

def setup(domain=None, user=None):
    logging.info('#### linuxmuster-linuxclient7 setup ####')

    if not realm.clearUserCache():
        return False

    if not _cleanOldDomainJoins():
        return False

    rc, domain = _findDomain(domain)
    if not rc:
        return False

    if user == None:
        user = constants.defaultDomainAdminUser

    if not _prepareNetworkConfiguration(domain):
        return False

    if not _deleteObsoleteFiles():
        return False

    if not templates.applyAll():
        return False

    if not _preparePam():
        return False

    if not _prepareServices():
        return False

    # Actually join domain!
    print()
    logging.info("#### Joining domain {} ####".format(domain))

    if not realm.join(domain, user):
        return False

    # copy server ca certificate in place
    # This will also make sure that the domain join actually worked;
    # mounting the sysvol will fail otherwise.
    if not _installCaCertificate(domain, user):
        return False

    if not _adjustSssdConfiguration(domain):
        return False

    # run a final test
    if not realm.verifyDomainJoin():
        return False

    print("\n\n")

    logging.info("#### SUCCESSFULLY joined domain {} ####".format(domain))

    return True

def status():
    logging.info('#### linuxmuster-linuxclient7 status ####')

    if not isSetup():
        logging.info("Not setup!")
        return False

    logging.info("Linuxmuster-linuxclient7 is setup!")
    logging.info("Testing if domain is joined...")

    logging.info("Checking joined domains")
    rc, joinedDomains = realm.getJoinedDomains()
    if not rc:
        return False

    print()
    logging.info("Joined domains:")
    for joinedDomain in joinedDomains:
        logging.info("* {}".format(joinedDomain))
    print()

    if len(joinedDomains) > 0 and not realm.verifyDomainJoin():
        print()
        # Give a little explination to our users :)
        print("\n================================================================================")
        print("This Computer is joined to a domain but it was not possible to authenticate to the domain controller.")
        print("There is an error with your domain join!")
        print("This happens when you reboot the client without creating an image.")
        print("Please try to re-join the domain using 'linuxmuster-linuxclient7 setup'.")
        print("================================================================================\n")
        return False

    print()

    logging.info('#### linuxmuster-linuxclient7 is fully setup and working! ####')

    return True

def upgrade():
    if not isSetup():
        logging.info("linuxmuster-linuxclient7 does not seem to be setup -> no upgrade is needed")
        return True

    logging.info('#### linuxmuster-linuxclient7 upgrade ####')
    if not config.upgrade():
        return False

    if not templates.applyAll():
        return False

    if not _prepareServices():
        return False

    if not _deleteObsoleteFiles():
        return False

    rc, joinedDomains = realm.getJoinedDomains()
    if not rc:
        return False
    
    for domain in joinedDomains:
        _adjustSssdConfiguration(domain)

    logging.info('#### linuxmuster-linuxclient7 upgrade SUCCESSFULL ####')
    return True

def clean():
    logging.info("#### linuxmuster-linuxclient7 clean ####")

    realm.clearUserCache()
    _cleanOldDomainJoins()

    # clean /etc/pam.d/common-session
    logging.info("Cleaning /etc/pam.d/common-session to prevent logon brick")
    fileHelper.removeLinesInFileContainingString("/etc/pam.d/common-session", ["pam_mkhomedir.so", "pam_exec.so", "pam_mount.so", "linuxmuster.net", "linuxmuster-linuxclient7"])

    logging.info('#### linuxmuster-linuxclient7 clean SUCCESSFULL ####')

def isSetup():
    return os.path.isfile(constants.networkConfigFilePath)

# --------------------
# - Helper functions -
# --------------------

def _cleanOldDomainJoins():
    # stop sssd
    logging.info("Stopping sssd")
    if os.system("service sssd stop") != 0:
        logging.error("Failed!")
        return False

    # Clean old domain join data
    logging.info("Deleting old kerberos tickets.")
    os.system("kdestroy 2> /dev/null")

    if not realm.leaveAll():
        return False

    # delete krb5.keytab file, if existent
    logging.info('Deleting krb5.keytab if it exists ... ')
    if not fileHelper.deleteFile("/etc/krb5.keytab"):
        return False

    # delete old CA Certificate
    logging.info('Deleting old CA certificate if it exists ... ')
    if not fileHelper.deleteFilesWithExtension("/var/lib/samba/private/tls", ".pem"):
        return False

    # remove network.conf
    logging.info("Deleting {} if exists ...".format(constants.networkConfigFilePath))
    if not fileHelper.deleteFile(constants.networkConfigFilePath):
        return False

    return True

def _findDomain(domain=None):
    logging.info("Trying to discover available domains...")
    rc, availableDomains = realm.discoverDomains()
    if not rc or len(availableDomains) < 1:
        logging.error("Could not discover any domain!")
        return False, None
    
    if domain == None:
        domain = availableDomains[0]
        logging.info("Using first discovered domain {}".format(domain))
    elif domain in availableDomains:
        logging.info("Using domain {}".format(domain))
    else:
        print("\n")
        logging.error("Could not find domain {}!".format(domain))
        return False, None
    
    return True, domain

def _prepareNetworkConfiguration(domain):
    logging.info("Preparing network configuration")
    rc, domainConfig = realm.getDomainConfig(domain)
    if not rc:
        logging.error("Could not read domain configuration")
        return False

    newNetworkConfig = {}
    newNetworkConfig["serverHostname"] = domainConfig["domain-controller"]
    newNetworkConfig["domain"] = domainConfig["domain-name"]
    newNetworkConfig["realm"] = domainConfig["domain-name"].upper()

    config.writeNetworkConfig(newNetworkConfig)

    return True

def _preparePam():
    # enable necessary pam modules
    logging.info('Updating pam configuration ... ')
    os.system('pam-auth-update --package --enable libpam-mount pwquality sss --force')
    ## mkhomedir was injected in template not using pam-auth-update
    os.system('pam-auth-update --package --remove krb5 mkhomedir --force')

    return True

def _prepareServices():
    logging.info('Enabling services:')
    services = ['linuxmuster-linuxclient7', 'smbd', 'nmbd', 'sssd']
    for service in services:
        logging.info('* %s' % service)
        os.system('systemctl enable ' + service + '.service')

    logging.info('Restarting services:')
    services = ['smbd', 'nmbd', 'systemd-timesyncd']
    for service in services:
        logging.info('* %s' % service)
        os.system('systemctl restart ' + service + '.service')

    return True

def _installCaCertificate(domain, user):
    logging.info('Installing server ca certificate ... ')

    # try to mount the share
    rc, sysvolMountpoint = shares.mountShare("//{}/sysvol".format(domain), shareName="sysvol", hiddenShare=True, username=user)
    if not rc:
        logging.error("Failed to mount sysvol!")
        return False

    cacertPath = sysvolMountpoint + "/{}/tls/cacert.pem".format(domain)
    cacertTargetPath = "/var/lib/samba/private/tls/{}.pem".format(domain)

    logging.info("Copying CA certificate from server to client!")
    try:
        os.system('mkdir -p "$(dirname ' + cacertTargetPath + ')"')
        os.system('cp ' + cacertPath + ' ' + cacertTargetPath)
    except Exception as e:
        logging.error("Failed!")
        logging.exception(e)
        return False

    # make sure the file was successfully copied
    if not os.path.isfile(cacertTargetPath):
        logging.error('Failed to copy over CA certificate!')
        return False

    # unmount sysvol
    shares.unmountAllSharesOfUser(user)

    return True

def _adjustSssdConfiguration(domain):
    logging.info("Adjusting sssd.conf")

    sssdConfigFilePath = '/etc/sssd/sssd.conf'
    sssdConfig = configparser.ConfigParser(interpolation=None)

    sssdConfig.read(sssdConfigFilePath)
    # accept usernames without domain
    sssdConfig["domain/{}".format(domain)]["use_fully_qualified_names"] = "False"

    # override homedir
    sssdConfig["domain/{}".format(domain)]["override_homedir"] = "/home/%u"

    # Don't validate KVNO! Otherwise the Login will fail when the KVNO stored 
    # in /etc/krb5.keytab does not match the one in the AD (msDS-KeyVersionNumber)
    sssdConfig["domain/{}".format(domain)]["krb5_validate"] = "False"

    sssdConfig["domain/{}".format(domain)]["ad_gpo_access_control"] = "permissive"
    sssdConfig["domain/{}".format(domain)]["ad_gpo_ignore_unreadable"] = "True"

    try:
        logging.info("Writing new Configuration")
        with open(sssdConfigFilePath, 'w') as sssdConfigFile:
            sssdConfig.write(sssdConfigFile)

    except Exception as e:
        logging.error("Failed!")
        logging.exception(e)
        return False

    logging.info("Restarting sssd")
    if os.system("service sssd restart") != 0:
        logging.error("Failed!")
        return False

    return True

def _deleteObsoleteFiles():
    
    # files
    logging.info("Deleting obsolete files")

    for obsoleteFile in constants.obsoleteFiles:
        logging.info("* {}".format(obsoleteFile))
        fileHelper.deleteFile(obsoleteFile)

    # directories
    logging.info("Deleting obsolete directories")

    for obsoleteDirectory in constants.obsoleteDirectories:
        logging.info("* {}".format(obsoleteDirectory))
        fileHelper.deleteDirectory(obsoleteDirectory)

    return True