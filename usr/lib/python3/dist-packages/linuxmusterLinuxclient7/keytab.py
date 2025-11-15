from krb5KeytabUtil import Krb5KeytabUtil
from linuxmusterLinuxclient7 import computer, config, logging

def patchKeytab():
    """
    Patches the `/etc/krb5.keytab` file. It inserts the correct hostname of the current computer.

    :return: True on success, False otherwise
    :rtype: bool
    """
    krb5KeytabFilePath = "/etc/krb5.keytab"
    logging.info(f"Patching {krb5KeytabFilePath}")
    krb5KeytabUtil = Krb5KeytabUtil(krb5KeytabFilePath)

    try:
        krb5KeytabUtil.read()
    except:
        logging.error(f"Error reading {krb5KeytabFilePath}")
        return False

    for entry in krb5KeytabUtil.keytab.entries:
        oldData = entry.principal.components[-1].data
        if len(entry.principal.components) == 1:
            newData = computer.hostname().upper() + "$"
            entry.principal.components[0].data = newData

        elif len(entry.principal.components) == 2 and entry.principal.components[0].data in ["host", "HOST", "RestrictedKrbHost"]:
            rc, networkConfig = config.network()
            if not rc:
                continue

            newData = ""
            domain = networkConfig["domain"]
            if entry.principal.components[0].data == "RestrictedKrbHost":
                newData = computer.hostname().lower() + "." + domain
            elif entry.principal.components[0].data == "HOST":
                newData = computer.hostname().upper() + "." + domain
            elif entry.principal.components[0].data == "host":
                newData = computer.hostname().upper()

            entry.principal.components[1].data = newData

        logging.debug(f"{oldData} was changed to {entry.principal.components[-1].data}")
    
    logging.info(f"Trying to overwrite {krb5KeytabFilePath}")
    try:
        result = krb5KeytabUtil.write()
    except:
        result = False

    if not result:
        logging.error(f"Error overwriting {krb5KeytabFilePath}")
    
    return result
