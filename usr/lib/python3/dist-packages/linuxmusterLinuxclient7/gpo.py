 # Order of parsing: (overwriting each other)
 # 1. Local (does not apply)
 # 2. Site (does not apply)
 # 3. Domain
 # 4. OUs from top to bottom
import ldap, ldap.sasl, re, os.path
import xml.etree.ElementTree as ElementTree
from linuxmusterLinuxclient7 import logging, constants, config, user, ldapHelper, shares, computer, printers

def processAllPolicies():
    """
    Process all applicable policies (equivalent to gpupdate on windows)

    :return: True on success, False otherwise
    :rtype: bool
    """    
    rc, policyDnList = _findApplicablePolicies()
    if not rc:
        logging.fatal("Error when loading applicable GPOs! Shares and printers will not work.")
        return False

    for policyDn in policyDnList:
        _parsePolicy(policyDn)

# --------------------
# - Helper functions -
# --------------------

def _parseGplinkSring(string):
    # a gPLink strink looks like this:
    # [LDAP://<link>;<status>][LDAP://<link>;<status>][...]
    # The ragex matches <link> and <status> in two separate groups
    # Note: "LDAP://" is matched as .*:// to prevent issues when the capitalization changes
    pattern = re.compile("\\[.*:\\/\\/([^\\]]+)\\;([0-9]+)\\]")

    return pattern.findall(string)

def _extractOUsFromDN(dn):
    # NOT finished!
    pattern = re.compile("OU=([^,]+),")

    ouList = pattern.findall(dn)
    # We need to parse from top to bottom
    ouList.reverse()
    return ouList

def _findApplicablePolicies():

    policyDnList = []

    """ Do this later!
    # 1. Domain
    rc, domainAdObject = ldapHelper.searchOne("(distinguishedName={})".format(ldapHelper.baseDn()))

    if not rc:
        return False, None

    policyDNs.extend(_parseGplinkSring(domainAdObject["gPLink"]))

    # 2. OU policies from top to bottom
    rc, userAdObject = ldapHelper.searchOne("(sAMAccountName={})".format(user.username()))

    if not rc:
        return False, None

    print(userAdObject["distinguishedName"])
    """

    # For now, just parse policy sophomorix:school:<school name>
    rc, schoolName = user.school()
    if not rc:
        return False, None

    policyName = "sophomorix:school:{}".format(schoolName)

    # find policy
    rc, policyAdObject = ldapHelper.searchOne("(displayName={})".format(policyName))
    if not rc:
        return False, None

    policyDnList.append((policyAdObject["distinguishedName"], 0))

    return True, policyDnList

def _parsePolicy(policyDn):
    logging.info("=== Parsing policy [{0};{1}] ===".format(policyDn[0], policyDn[1]))

    # Check if the policy is disabled
    if policyDn[1] == 1:
        logging.info("===> Policy is disabled! ===")
        return True

    # Find policy in AD
    rc, policyAdObject = ldapHelper.searchOne("(distinguishedName={})".format(policyDn[0]))
    if not rc:
        logging.error("===> Could not find poilcy in AD! ===")
        return False, None

    # mount the share the policy is on (probaply already mounted, just to be sure)
    rc, localPolicyPath = shares.getMountpointOfRemotePath(policyAdObject["gPCFileSysPath"], hiddenShare = True, autoMount = True)
    if not rc:
        logging.error("===> Could not mount path of poilcy! ===")
        return False, None

    try:
        # parse drives
        _processDrivesPolicy(localPolicyPath)
        # parse printers
        _processPrintersPolicy(localPolicyPath)
    except Exception as e:
        logging.error("An error occured when parsing policy!")
        logging.exception(e)
    
    logging.info("===> Parsed policy [{0};{1}] ===".format(policyDn[0], policyDn[1]))

def _parseXmlFilters(filtersXmlNode):
    if not filtersXmlNode.tag == "Filters":
        logging.warning("Tried to parse a non-filter node as a filter!")
        return []

    filters = []

    for xmlFilter in filtersXmlNode:
        if xmlFilter.tag == "FilterGroup":
            filters.append({
                "name": xmlFilter.attrib["name"].split("\\")[1],
                "bool": xmlFilter.attrib["bool"],
                "userContext": xmlFilter.attrib["userContext"],
                # userContext defines if the filter applies in user or computer context
                "type": xmlFilter.tag
                })

    return filters

def _processFilters(policies):
    filteredPolicies = []

    for policy in policies:
        if  not len(policy["filters"]) > 0:
            filteredPolicies.append(policy)
        else:
            filtersPassed = True
            for filter in policy["filters"]:
                logging.debug("Testing filter: {}".format(filter))
                # TODO: check for AND and OR
                if filter["bool"] == "AND":
                    filtersPassed = filtersPassed and _processFilter(filter)
                elif filter["bool"] == "OR":
                    filtersPassed = filtersPassed or _processFilter(filter)
                else:
                    logging.warning("Unknown boolean operation: {}! Cannot process filter!".format(filter["bool"]))

            if filtersPassed:
                filteredPolicies.append(policy)

    return filteredPolicies

def _processFilter(filter):
    if filter["type"] == "FilterGroup":
        if filter["userContext"] == "1":
            return user.isInGroup(filter["name"])
        elif filter["userContext"] == "0":
            return computer.isInGroup(filter["name"])

    return False

def _parseXmlPolicy(policyFile):
    if not os.path.isfile(policyFile):
        logging.warning("==> XML policy file not found! ==")
        return False, None

    try:
        tree = ElementTree.parse(policyFile)
        return True, tree
    except Exception as e:
        logging.exception(e)
        logging.error("==> Error while reading XML policy file! ==")
        return False, None

def _processDrivesPolicy(policyBasepath):
    logging.info("== Parsing a drive policy! ==")
    policyFile = "{}/User/Preferences/Drives/Drives.xml".format(policyBasepath)
    shareList = []

    rc, tree = _parseXmlPolicy(policyFile)

    if not rc:
        logging.error("==> Error while reading Drives policy file, skipping! ==")
        return

    xmlDrives = tree.getroot()

    if not xmlDrives.tag == "Drives":
        logging.warning("==> Drive policy xml File is of invalid format, skipping! ==")
        return

    for xmlDrive in xmlDrives:

        if xmlDrive.tag != "Drive" or ("disabled" in xmlDrive.attrib and xmlDrive.attrib["disabled"] == "1"):
            continue

        drive = {}
        drive["filters"] = []
        for xmlDriveProperty in xmlDrive:
            if xmlDriveProperty.tag == "Properties":
                try:
                    drive["label"] = xmlDriveProperty.attrib["label"]
                    drive["letter"] = xmlDriveProperty.attrib["letter"]
                    drive["path"] = xmlDriveProperty.attrib["path"]
                    drive["useLetter"] = xmlDriveProperty.attrib["useLetter"]
                except Exception as e:
                    logging.warning("Exception when parsing a drive policy XML file")
                    logging.exception(e)
                    continue

            if xmlDriveProperty.tag == "Filters":
                drive["filters"] = _parseXmlFilters(xmlDriveProperty)

        shareList.append(drive)

    shareList = _processFilters(shareList)

    logging.info("Found shares:")
    for drive in shareList:
        logging.info("* {:10}| {:5}| {:40}| {:5}".format(drive["label"], drive["letter"], drive["path"], drive["useLetter"]))

    for drive in shareList:
        if drive["useLetter"] == "1":
            shareName = f"{drive['label']} ({drive['letter']}:)"  
        else:
             drive["label"]
        shares.mountShare(drive["path"], shareName=shareName)

    logging.info("==> Successfully parsed a drive policy! ==")

def _processPrintersPolicy(policyBasepath):
    logging.info("== Parsing a printer policy! ==")
    policyFile = "{}/User/Preferences/Printers/Printers.xml".format(policyBasepath)
    printerList = []
    # test
    rc, tree = _parseXmlPolicy(policyFile)

    if not rc:
        logging.error("==> Error while reading Printer policy file, skipping! ==")
        return

    xmlPrinters = tree.getroot()

    if not xmlPrinters.tag == "Printers":
        logging.warning("==> Printer policy xml File is of invalid format, skipping! ==")
        return

    for xmlPrinter in xmlPrinters:

        if xmlPrinter.tag != "SharedPrinter" or ("disabled" in xmlPrinter.attrib and xmlPrinter.attrib["disabled"] == "1"):
            continue

        printer = {}
        printer["filters"] = []

        try:
            printer["name"] = xmlPrinter.attrib["name"]
        except Exception as e:
            logging.warning("Exception when reading a printer name from a printer policy XML file")
            logging.exception(e)

        for xmlPrinterProperty in xmlPrinter:
            if xmlPrinterProperty.tag == "Properties":
                try:
                    rc, printerUrl = printers.translateSambaToIpp(xmlPrinterProperty.attrib["path"])
                    if rc:
                        printer["path"] = printerUrl
                except Exception as e:
                    logging.warning("Exception when parsing a printer policy XML file")
                    logging.exception(e)
                    continue

            if xmlPrinterProperty.tag == "Filters":
                printer["filters"] = _parseXmlFilters(xmlPrinterProperty)

        printerList.append(printer)

    printerList = _processFilters(printerList)

    logging.info("Found printers:")
    for printer in printerList:
        logging.info("* {0}\t\t| {1}\t| {2}".format(printer["name"], printer["path"], printer["filters"]))
        printers.installPrinter(printer["path"], printer["name"])

    logging.info("==> Successfully parsed a printer policy! ==")