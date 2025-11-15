from unittest import mock
from .. import gpo
import os

@mock.patch("linuxmusterLinuxclient7.gpo.computer.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.user.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.printers.installPrinter")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.mountShare")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.getMountpointOfRemotePath")
@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_allOkAllTrue(mockUserSchool, mockLdapHelperSearchOne, mockSharesGetMountpointOfRemotePath, mockSharesmMountShare, mockPrintersInstallPrinter, mockUserIsInGroup, mockComputerIsInGroup):
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (True, {
        "distinguishedName": "policy1",
        "gPCFileSysPath": "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"
    })
    mockSharesGetMountpointOfRemotePath.return_value = (True, f"{os.path.dirname(os.path.realpath(__file__))}/files/policy1")
    mockSharesmMountShare.return_value = (True, "")
    mockPrintersInstallPrinter.return_value = True
    mockUserIsInGroup.return_value = True
    mockComputerIsInGroup.return_value = True

    # Drives: /User/Preferences/Drives/Drives.xml
    # Printers: /User/Preferences/Printers/Printers.xml

    assert gpo.processAllPolicies()

    assert mockLdapHelperSearchOne.call_args_list[0].args[0] == "(displayName=sophomorix:school:school1)"
    assert mockLdapHelperSearchOne.call_args_list[1].args[0] == "(distinguishedName=policy1)"
    assert mockSharesGetMountpointOfRemotePath.call_args_list[0].args[0] == "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"

    # Check shares
    assert mockUserIsInGroup.call_args_list[0].args[0] == "teachers"
    assert len(mockSharesmMountShare.call_args_list) == 3
    assert mockSharesmMountShare.call_args_list[0] == mock.call('\\\\server\\default-school\\program', shareName='Programs (K:)')
    # Projects (P:) is disabled and should not be mounted
    assert mockSharesmMountShare.call_args_list[1] == mock.call('\\\\server\\default-school\\students', shareName='Students-Home (S:)')
    assert mockSharesmMountShare.call_args_list[2] == mock.call('\\\\server\\default-school\\share', shareName='Shares')

    # Check printers
    assert mockUserIsInGroup.call_args_list[1].args[0] == "printer1"
    # computer.isInGroup does not have to be called, because it is 
    # an or condition and the user is already in the group.
    # assert mockComputerIsInGroup.call_args_list[1].args[0] == "printer1"
    assert len(mockPrintersInstallPrinter.call_args_list) == 1
    assert mockPrintersInstallPrinter.call_args_list[0] == mock.call('ipp://SERVER/printers/PRINTER1', 'PRINTER1')

@mock.patch("linuxmusterLinuxclient7.gpo.config.shares")
@mock.patch("linuxmusterLinuxclient7.gpo.computer.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.user.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.printers.installPrinter")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.mountShare")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.getMountpointOfRemotePath")
@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_customShareNameTemplate(mockUserSchool, mockLdapHelperSearchOne, mockSharesGetMountpointOfRemotePath, mockSharesmMountShare, mockPrintersInstallPrinter, mockUserIsInGroup, mockComputerIsInGroup, mockConfigShares):
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (True, {
        "distinguishedName": "policy1",
        "gPCFileSysPath": "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"
    })
    mockSharesGetMountpointOfRemotePath.return_value = (True, f"{os.path.dirname(os.path.realpath(__file__))}/files/policy1")
    mockSharesmMountShare.return_value = (True, "")
    mockPrintersInstallPrinter.return_value = True
    mockUserIsInGroup.return_value = True
    mockComputerIsInGroup.return_value = True
    mockConfigShares.return_value = {
        "nameTemplate": "{label}_{letter}"
    }

    assert gpo.processAllPolicies()
    assert len(mockSharesmMountShare.call_args_list) == 3
    assert mockSharesmMountShare.call_args_list[0] == mock.call('\\\\server\\default-school\\program', shareName='Programs_K')
    # Projects (P:) is disabled and should not be mounted
    assert mockSharesmMountShare.call_args_list[1] == mock.call('\\\\server\\default-school\\students', shareName='Students-Home_S')
    assert mockSharesmMountShare.call_args_list[2] == mock.call('\\\\server\\default-school\\share', shareName='Shares')

    # Test without letter
    mockConfigShares.return_value = {
        "nameTemplate": "{label}"
    }
    assert gpo.processAllPolicies()
    assert len(mockSharesmMountShare.call_args_list) == 6
    assert mockSharesmMountShare.call_args_list[3] == mock.call('\\\\server\\default-school\\program', shareName='Programs')
    # Projects (P:) is disabled and should not be mounted
    assert mockSharesmMountShare.call_args_list[4] == mock.call('\\\\server\\default-school\\students', shareName='Students-Home')
    assert mockSharesmMountShare.call_args_list[5] == mock.call('\\\\server\\default-school\\share', shareName='Shares')

@mock.patch("linuxmusterLinuxclient7.gpo.computer.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.user.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.printers.installPrinter")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.mountShare")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.getMountpointOfRemotePath")
@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_allOkUserInGroupFalse(mockUserSchool, mockLdapHelperSearchOne, mockSharesGetMountpointOfRemotePath, mockSharesmMountShare, mockPrintersInstallPrinter, mockUserIsInGroup, mockComputerIsInGroup):
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (True, {
        "distinguishedName": "policy1",
        "gPCFileSysPath": "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"
    })
    mockSharesGetMountpointOfRemotePath.return_value = (True, f"{os.path.dirname(os.path.realpath(__file__))}/files/policy1")
    mockSharesmMountShare.return_value = (True, "")
    mockPrintersInstallPrinter.return_value = True
    mockUserIsInGroup.return_value = False
    mockComputerIsInGroup.return_value = True

    assert gpo.processAllPolicies()

    # Checks which are already done in other tests are not needed again

    # Check shares
    assert mockUserIsInGroup.call_args_list[0].args[0] == "teachers"
    assert len(mockSharesmMountShare.call_args_list) == 2
    assert mockSharesmMountShare.call_args_list[0] == mock.call('\\\\server\\default-school\\program', shareName='Programs (K:)')
    # Projects (P:) is disabled and should not be mounted
    # User is not member of teachers assert mockSharesmMountShare.call_args_list[1] == mock.call('\\\\server\\default-school\\students', shareName='Students-Home (S:)')
    assert mockSharesmMountShare.call_args_list[1] == mock.call('\\\\server\\default-school\\share', shareName='Shares')

    # Check printers
    assert mockUserIsInGroup.call_args_list[1].args[0] == "printer1"
    assert mockComputerIsInGroup.call_args_list[0].args[0] == "printer1"
    assert len(mockPrintersInstallPrinter.call_args_list) == 1
    assert mockPrintersInstallPrinter.call_args_list[0] == mock.call('ipp://SERVER/printers/PRINTER1', 'PRINTER1')

@mock.patch("linuxmusterLinuxclient7.gpo.computer.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.user.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.printers.installPrinter")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.mountShare")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.getMountpointOfRemotePath")
@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_allOkUserInGroupFalseComputerInGroupFalse(mockUserSchool, mockLdapHelperSearchOne, mockSharesGetMountpointOfRemotePath, mockSharesmMountShare, mockPrintersInstallPrinter, mockUserIsInGroup, mockComputerIsInGroup):
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (True, {
        "distinguishedName": "policy1",
        "gPCFileSysPath": "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"
    })
    mockSharesGetMountpointOfRemotePath.return_value = (True, f"{os.path.dirname(os.path.realpath(__file__))}/files/policy1")
    mockSharesmMountShare.return_value = (True, "")
    mockPrintersInstallPrinter.return_value = True
    mockUserIsInGroup.return_value = False
    mockComputerIsInGroup.return_value = False

    assert gpo.processAllPolicies()

    # Checks which are already done in other tests are not needed again

    # Check printers
    assert mockUserIsInGroup.call_args_list[1].args[0] == "printer1"
    assert mockComputerIsInGroup.call_args_list[0].args[0] == "printer1"
    assert len(mockPrintersInstallPrinter.call_args_list) == 0
    # Printer should not be applied assert mockPrintersInstallPrinter.call_args_list[0] == mock.call('ipp://SERVER/printers/PRINTER1', 'PRINTER1')

@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_userSchoolError(mockUserSchool):
    mockUserSchool.return_value = (False, None)

    assert not gpo.processAllPolicies()

@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_ldapSearchOneErrorFirst(mockUserSchool, mockLdapHelperSearchOne):
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (False, None)

    assert not gpo.processAllPolicies()

@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_ldapSearchOneErrorSecond(mockUserSchool, mockLdapHelperSearchOne):
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.side_effect = [(True, {
        "distinguishedName": "policy1"
    }), (False, None)]
    
    assert not gpo.processAllPolicies()

@mock.patch("linuxmusterLinuxclient7.gpo.shares.getMountpointOfRemotePath")
@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_sharesGetMountpointOfRemotePathError(mockUserSchool, mockLdapHelperSearchOne, mockSharesGetMountpointOfRemotePath):
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (True, {
        "distinguishedName": "policy1",
        "gPCFileSysPath": "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"
    })
    mockSharesGetMountpointOfRemotePath.return_value = (False, None)

    assert not gpo.processAllPolicies()

@mock.patch("linuxmusterLinuxclient7.gpo.shares.getMountpointOfRemotePath")
@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_policyPathInvalid(mockUserSchool, mockLdapHelperSearchOne, mockSharesGetMountpointOfRemotePath):
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (True, {
        "distinguishedName": "policy1",
        "gPCFileSysPath": "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"
    })
    mockSharesGetMountpointOfRemotePath.return_value = (True, "/tmp/thisFolderDoesNotExist")

    assert not gpo.processAllPolicies()

@mock.patch("linuxmusterLinuxclient7.gpo.shares.getMountpointOfRemotePath")
@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_policyXmlRootTagIncorrect(mockUserSchool, mockLdapHelperSearchOne, mockSharesGetMountpointOfRemotePath):
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (True, {
        "distinguishedName": "policy1",
        "gPCFileSysPath": "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"
    })
    mockSharesGetMountpointOfRemotePath.return_value = (True, f"{os.path.dirname(os.path.realpath(__file__))}/files/policy-invalid1")

    assert not gpo.processAllPolicies()

@mock.patch("linuxmusterLinuxclient7.gpo.shares.getMountpointOfRemotePath")
@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_policyXmlInvalidFormatAndInvalidFilters(mockUserSchool, mockLdapHelperSearchOne, mockSharesGetMountpointOfRemotePath):
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (True, {
        "distinguishedName": "policy1",
        "gPCFileSysPath": "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"
    })
    mockSharesGetMountpointOfRemotePath.return_value = (True, f"{os.path.dirname(os.path.realpath(__file__))}/files/policy-invalid3")

    assert not gpo.processAllPolicies()

@mock.patch("linuxmusterLinuxclient7.gpo.computer.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.user.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.printers.installPrinter")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.mountShare")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.getMountpointOfRemotePath")
@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_policyXmlMissingAttributes(mockUserSchool, mockLdapHelperSearchOne, mockSharesGetMountpointOfRemotePath, mockSharesmMountShare, mockPrintersInstallPrinter, mockUserIsInGroup, mockComputerIsInGroup):
    # Programs (K:) is missing the label
    # PRINTER1 is missing the name
    # PRINTER2 is missing the path
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (True, {
        "distinguishedName": "policy1",
        "gPCFileSysPath": "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"
    })
    mockSharesGetMountpointOfRemotePath.return_value = (True, f"{os.path.dirname(os.path.realpath(__file__))}/files/policy-invalid2")
    mockSharesmMountShare.return_value = (True, "")
    mockPrintersInstallPrinter.return_value = True
    mockUserIsInGroup.return_value = True
    mockComputerIsInGroup.return_value = True

    assert gpo.processAllPolicies()

    # Check shares
    assert mockUserIsInGroup.call_args_list[0].args[0] == "teachers"
    assert len(mockSharesmMountShare.call_args_list) == 2
    # Programs (K:) is invalid assert mockSharesmMountShare.call_args_list[0] == mock.call('\\\\server\\default-school\\program', shareName='Programs (K:)')
    # Projects (P:) is disabled and should not be mounted
    assert mockSharesmMountShare.call_args_list[0] == mock.call('\\\\server\\default-school\\students', shareName='Students-Home (S:)')
    assert mockSharesmMountShare.call_args_list[1] == mock.call('\\\\server\\default-school\\share', shareName='Shares')

    # Check printers
    assert mockUserIsInGroup.call_args_list[1].args[0] == "printer3"
    assert len(mockPrintersInstallPrinter.call_args_list) == 1
    assert mockPrintersInstallPrinter.call_args_list[0] == mock.call('ipp://SERVER/printers/PRINTER3', 'PRINTER3')

@mock.patch("linuxmusterLinuxclient7.gpo.computer.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.user.isInGroup")
@mock.patch("linuxmusterLinuxclient7.gpo.printers.installPrinter")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.mountShare")
@mock.patch("linuxmusterLinuxclient7.gpo.shares.getMountpointOfRemotePath")
@mock.patch("linuxmusterLinuxclient7.gpo.ldapHelper.searchOne")
@mock.patch("linuxmusterLinuxclient7.gpo.user.school")
def test_sharesMountShareException(mockUserSchool, mockLdapHelperSearchOne, mockSharesGetMountpointOfRemotePath, mockSharesmMountShare, mockPrintersInstallPrinter, mockUserIsInGroup, mockComputerIsInGroup):
    # Programs (K:) is missing the label
    # PRINTER1 is missing the name
    # PRINTER2 is missing the path
    mockUserSchool.return_value = (True, "school1")
    mockLdapHelperSearchOne.return_value = (True, {
        "distinguishedName": "policy1",
        "gPCFileSysPath": "\\\\linuxmuster.lan\\sysvol\\linuxmuster.lan\\Policies\\policy1"
    })
    mockSharesGetMountpointOfRemotePath.return_value = (True, f"{os.path.dirname(os.path.realpath(__file__))}/files/policy-invalid2")
    mockSharesmMountShare.side_effect = Exception()

    mockPrintersInstallPrinter.return_value = True
    mockUserIsInGroup.return_value = True
    mockComputerIsInGroup.return_value = True

    assert not gpo.processAllPolicies()