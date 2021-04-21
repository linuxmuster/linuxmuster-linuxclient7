import ldap, ldap.sasl, sys, getpass, subprocess
from linuxmusterLinuxclient7 import logging, constants, config, user

_currentLdapConnection = None

def serverUrl():
    rc, networkConfig = config.network()

    if not rc:
        return False, None

    serverHostname = networkConfig["serverHostname"]
    return 'ldap://{0}'.format(serverHostname)

def baseDn():
    rc, networkConfig = config.network()

    if not rc:
        return None

    domain = networkConfig["domain"]
    return "dc=" + domain.replace(".", ",dc=")

def conn():
    global _currentLdapConnection

    if _connect():
        return _currentLdapConnection
    
    return None

def searchOne(filter):
    if conn() == None:
        logging.error("Cannot talk to LDAP")
        return False, None

    try:
        rawResult = conn().search_s(
                baseDn(),
                ldap.SCOPE_SUBTREE,
                filter
                )
    except Exception as e:
        logging.error("Error executing LDAP search!")
        logging.exception(e)
        return False, None

    try:
        result =  {}

        if len(rawResult) <= 0 or rawResult[0][0] == None:
            logging.debug("Search \"{}\" did not return any objects".format(filter))
            return False, None

        for k in rawResult[0][1]:
            if k != 'objectSid' and k != 'objectGUID' and rawResult[0][1][k] != None:
                rawAttribute = rawResult[0][1][k]
                if len(rawAttribute) == 1:
                    result[k] = str(rawAttribute[0].decode())
                elif len(rawAttribute) > 0:
                    result[k] = []
                    for rawItem in rawAttribute:
                        result[k].append(str(rawItem.decode()))
                #print(k, str(rawResult[0][1][k]))
                
        #print(result)
        return True, result

    except Exception as e:
        logging.error("Error while reading ldap search results!")
        logging.exception(e)
        return False, None

def isObjectInGroup(objectDn, groupName):
    logging.debug("= Testing if object {0} is a member of group {1} =".format(objectDn, groupName))
    rc, groupAdObject = searchOne("(&(member:1.2.840.113556.1.4.1941:={0})(sAMAccountName={1}))".format(objectDn, groupName))
    logging.debug("=> Result: {} =".format(rc))
    return rc

# --------------------
# - Helper functions -
# --------------------

def _connect():
    global _currentLdapConnection

    if not user.isInAD():
        logging.warning("Cannot perform LDAP search: User is not in AD!")
        _currentLdapConnection = None
        return False

    if not _currentLdapConnection == None:
        return True

    try:
        sasl_auth = ldap.sasl.sasl({} ,'GSSAPI')
        _currentLdapConnection = ldap.initialize(serverUrl(), trace_level=0)
        # TODO:
        # conn.set_option(ldap.OPT_X_TLS_CACERTFILE, '/path/to/ca.pem')
        # conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
        # conn.start_tls_s()
        _currentLdapConnection.set_option(ldap.OPT_REFERRALS,0)
        _currentLdapConnection.protocol_version = ldap.VERSION3

        _currentLdapConnection.sasl_interactive_bind_s("", sasl_auth)
    except Exception as e:
        _currentLdapConnection = None
        logging.error("Cloud not bind to ldap!")
        logging.exception(e)
        return False

    return True