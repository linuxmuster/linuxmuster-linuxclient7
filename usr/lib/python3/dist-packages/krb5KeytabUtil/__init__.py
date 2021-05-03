import binascii

class Krb5KeytabUtil:
    """
    A class to parse and create krb5keytab content.

    Attributes
    ----------
    debugLogs: bool
        Show debug logs when parsing (static)
    filePath: str
        The path to the file containing the keytab
    keytab: Krb5Keytab
        A Krb5Keytab object, which is read from filePath by read() and written to filePath by write()

    Methods
    -------
    read()
        Reads the contents of the file at filePath and puts them into keytab
    write()
        Takes keytab, converts it to binary and writes it to filePath
    """
    debugLogs = False

    def __init__(self, filePath, debugLogs = False):
        Krb5KeytabUtil._debugLogs = debugLogs
        self.filePath = filePath
        self.keytab = None

    def read(self):
        f = open(self.filePath, 'rb').read()

        # Convert to a long hex string
        fileContentsHex = binascii.hexlify(f).decode('utf-8')

        # Split the hex string into a list of bytes
        hexData = [fileContentsHex[i:i+2] for i in range(0, len(fileContentsHex), 2)]

        # Parse
        self.keytab = Krb5Keytab.fromHex(hexData)

    def write(self):
        if self.keytab == None:
            return False

        f = open(self.filePath, 'wb')
        f.write(self.keytab.toBytes())

        return True

    @staticmethod
    def _takeBytes(hexData, numBytes, join = True):
        retData = []
        for i in range(numBytes):
            retData.append(hexData.pop(0))

        if join:
            retData = "".join(retData)

        return retData

    @staticmethod
    def _debug(*m):
        if Krb5KeytabUtil.debugLogs:
            print(" ".join(map(str,m)))

class Krb5Keytab:
    """
    A class to parse and create krb5keytab content.

    From Kerberos documentation:
    keytab ::=
        kerberos version (8 bits)
        keytab version (8 bits)
        entry1 length (32 bits)
        entry1 (entry1 length bytes)
        entry2 length (32 bits)
        entry2 (entry2 length bytes)
        
    Attributes
    ----------
    entries: list
        A list of Krb5Keytab objects which are contained in this keytab

    Methods
    -------
    print()
        Prints the contents of this keytab in a style similar to `klist -k -K -t`
    toHex()
        Converts the Krb5Keytab object to a hex string
    toBytes()
        Converts the Krb5Keytab to a bytes object
    fromHex(hexData)
        Creates a Krb5Keytab object from a hex string
    """

    # Compatible keytab version
    _keytabVersion = "0502"

    def __init__(self):
        pass

    def print(self):
        for entry in self.entries:
            entry.print()

    def toHex(self):
        return self.toBytes().hex()

    def toBytes(self):
        result = bytes()

        result += bytes.fromhex(Krb5Keytab._keytabVersion)

        for entry in self.entries:
            entryBytes = entry.toBytes()
            result += len(entryBytes).to_bytes(4, byteorder='big')
            result += entryBytes
        
        return result

    @staticmethod 
    def fromHex(hexData):
        tmpKeytab = Krb5Keytab()
        keytabVersion = Krb5KeytabUtil._takeBytes(hexData, 2)
        Krb5KeytabUtil._debug("[*] Found keytab version " + str(keytabVersion))
        if not keytabVersion == Krb5Keytab._keytabVersion:
            Krb5KeytabUtil._debug("-> Not compatible!")
            return False, None

        tmpKeytab.entries = []
        while len(hexData) > 0:
            Krb5KeytabUtil._debug("")
            Krb5KeytabUtil._debug("Tyring to parse new entry:")
            entryLength = int(Krb5KeytabUtil._takeBytes(hexData, 4), 16)
            Krb5KeytabUtil._debug("* Entry length: ", entryLength)

            entryData = Krb5KeytabUtil._takeBytes(hexData, entryLength, False)

            tmpKeytab.entries.append(Krb5Entry.fromHex(entryData, tmpKeytab))

        return tmpKeytab

class Krb5Entry:
    """
    A class to parse and create krb5keytab entry blocks.

    From Kerberos documentation:
    entry ::=
        principal
        timestamp (32 bits)
        key version (8 bits)
        enctype (16 bits)
        key length (32 bits)
                    16 ??
        key contents

    Attributes
    ----------
    principal: Krb5Principal
        A Krb5Principal object which is the principal of this entry
    timstamp: int
        The timestamp of when this entry was created
    keyVersion: int
        The key version of this entry (KVNO)
    encType: int
        The encryption type of this entry
    keyContents: str
        The key contents of this entry as hex

    Methods
    -------
    print()
        Prints the contents of this entry in a style similar to `klist -k -K -t`
    toHex()
        Converts the Krb5Entry object to a hex string
    toBytes()
        Converts the Krb5Entry to a bytes object
    fromHex(hexData)
        Creates a Krb5Entry object from a hex string
    """

    def __init__(self):
        pass

    def print(self):
        componentData = []
        for component in self.principal.components:
            componentData.append(component.data)
        print(self.keyVersion, self.timestamp, "/".join(componentData) + "@" + self.principal.realm.data, "(0x" + self.keyContents + ")")

    def toHex(self):
        return self.toBytes().hex()

    def toBytes(self):
        result = bytes()

        result += self.principal.toBytes()
        result += self.timestamp.to_bytes(4, byteorder='big')
        result += self.keyVersion.to_bytes(1, byteorder='big')
        result += self.encType.to_bytes(2, byteorder='big')

        keyContentsBytes = bytes.fromhex(self.keyContents)
        result += len(keyContentsBytes).to_bytes(2, byteorder='big')
        result += keyContentsBytes

        return result

    @staticmethod
    def fromHex(hexData, parser):
        tmpEntry = Krb5Entry()
        tmpEntry._parser = parser

        Krb5KeytabUtil._debug("# Parsing keytab entry")

        tmpEntry.principal = Krb5Principal.fromHex(hexData, tmpEntry._parser)

        tmpEntry.timestamp = int(Krb5KeytabUtil._takeBytes(hexData, 4), 16)
        Krb5KeytabUtil._debug("* Timestamp: ", tmpEntry.timestamp)

        tmpEntry.keyVersion = int(Krb5KeytabUtil._takeBytes(hexData, 1), 16)
        Krb5KeytabUtil._debug("* Key version: ", tmpEntry.keyVersion)

        tmpEntry.encType = int(Krb5KeytabUtil._takeBytes(hexData, 2), 16)
        Krb5KeytabUtil._debug("* Enc type: ", tmpEntry.encType)

        keyLength = int(Krb5KeytabUtil._takeBytes(hexData, 2), 16)
        Krb5KeytabUtil._debug("* Key length: ", keyLength)

        tmpEntry.keyContents = Krb5KeytabUtil._takeBytes(hexData, keyLength)
        Krb5KeytabUtil._debug("* Key contents: ", tmpEntry.keyContents)

        return tmpEntry

class Krb5Principal:
    """
    A class to parse and create krb5keytab principal blocks.

    From Kerberos documentation:
    principal ::=
        count of components (32 bits) [does not include realm]
                             16 ????
        realm (data)
        component1 (data)
        component2 (data)
        ...
        name type (32 bits)

    Attributes
    ----------
    realm: Krb5Data
        A Krb5Data object which is the realm of this principal
    components: list
        A list of Krb5Data objects which are the components of this principal
    nameType: str
        The name type as hex string

    Methods
    -------
    toHex()
        Converts the Krb5Principal object to a hex string
    toBytes()
        Converts the Krb5Principal to a bytes object
    fromHex(hexData)
        Creates a Krb5Principal object from a hex string
    """

    def __init__(self):
        pass

    def toHex(self):
        return self.toBytes().hex()

    def toBytes(self):
        result = bytes()

        result += len(self.components).to_bytes(2, byteorder='big')
        result += self.realm.toBytes()

        for component in self.components:
            result += component.toBytes()

        result += bytes.fromhex(self.nameType)

        return result

    @staticmethod
    def fromHex(hexData, parser):
        tmpPrincipal = Krb5Principal()
        Krb5KeytabUtil._debug("## Parsing a principal block")

        countOfComponents = int(Krb5KeytabUtil._takeBytes(hexData, 2), 16)
        Krb5KeytabUtil._debug("** Count of components (excluding realm): ",  countOfComponents)

        # realm is not included in count of components
        tmpPrincipal.realm = Krb5Data.fromHex(hexData)

        tmpPrincipal.components = []
        for i in range(countOfComponents):
            tmpPrincipal.components.append(Krb5Data.fromHex(hexData))

        tmpPrincipal.nameType = Krb5KeytabUtil._takeBytes(hexData, 4)
        Krb5KeytabUtil._debug("** Name type: ", tmpPrincipal.nameType)

        return tmpPrincipal

class Krb5Data:
    """
    A class to parse and create krb5keytab data blocks.

    From Kerberos documentation:
    data ::=
        length (16 bits)
        value (length bytes)

    Attributes
    ----------
    data: str
        The data the block contains

    Methods
    -------
    toHex()
        Converts the Krb5Data object to a hex string
    toBytes()
        Converts the Krb5Data object to a bytes object
    fromHex(hexData)
        Creates a Krb5Data object from a hex string
    """

    def __init__(self):
        pass

    def toHex(self):
        return self.toBytes().hex()

    def toBytes(self):
        result = bytes()

        dataBytes = bytes(self.data, 'utf-8')
        result += len(dataBytes).to_bytes(2, byteorder='big')
        result += dataBytes

        return result

    @staticmethod
    def fromHex(hexData):
        tmpData = Krb5Data()
        Krb5KeytabUtil._debug("### Parsing a data block")

        length = int(Krb5KeytabUtil._takeBytes(hexData, 2), 16)
        Krb5KeytabUtil._debug("*** Length: ", length)

        tmpData.data = bytes.fromhex(Krb5KeytabUtil._takeBytes(hexData, length)).decode('utf-8')
        Krb5KeytabUtil._debug("*** Data: ", tmpData.data)

        return tmpData