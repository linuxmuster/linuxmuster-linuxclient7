from krb5KeytabUtil import Krb5KeytabUtil
from linuxmusterLinuxclient7 import computer, config, logging

def patchKeytab():
    krb5KeytabFilePath = "/etc/krb5.keytab"
    logging.info("Patching {}".format(krb5KeytabFilePath))
    krb5KeytabUtil = Krb5KeytabUtil(krb5KeytabFilePath)

    try:
        krb5KeytabUtil.read()
    except:
        logging.error("Error reading {}".format(krb5KeytabFilePath))
        return False

    for entry in krb5KeytabUtil.keytab.entries:
        oldData = entry.principal.components[-1].data
        if len(entry.principal.components) == 1:
            newData = computer.hostname().upper() + "$"
            entry.principal.components[0].data = newData

        elif len(entry.principal.components) == 2 and (entry.principal.components[0].data == "host" or entry.principal.components[0].data == "RestrictedKrbHost"):
            rc, networkConfig = config.network()
            if not rc:
                continue

            newData = ""
            domain = networkConfig["domain"]
            if domain in entry.principal.components[1].data:
                newData = computer.hostname().lower() + "." + domain
            else:
                newData = computer.hostname().upper()

            entry.principal.components[1].data = newData

        logging.debug("{} was changed to {}".format(oldData, entry.principal.components[-1].data))
    
    logging.info("Trying to overwrite {}".format(krb5KeytabFilePath))
    try:
        result = krb5KeytabUtil.write()
    except:
        result = False

    if not result:
        logging.error("Error overwriting {}".format(krb5KeytabFilePath))
    
    return result
