from unittest import mock
from .. import fileHelper
import os

def test_removeLinesInFileContainingString():
    assert fileHelper.deleteFile("/tmp/fileWithForbiddenLine")

    # unreadable file
    assert not fileHelper.removeLinesInFileContainingString("/tmp", "forbidden")

    with open("/tmp/fileWithForbiddenLine", "w") as file:
        file.write("line1\nforbidden line2\nline3")

    # unwritable file
    os.chmod("/tmp/fileWithForbiddenLine", 0o444)
    assert not fileHelper.removeLinesInFileContainingString("/tmp/fileWithForbiddenLine", "forbidden")

    # all fine
    os.chmod("/tmp/fileWithForbiddenLine", 0o666)
    assert fileHelper.removeLinesInFileContainingString("/tmp/fileWithForbiddenLine", "forbidden")

def test_deleteFile():

    assert fileHelper.deleteFile("/tmp/thisFileDoesNotExist")

    with open("/tmp/thisFileShouldBeDeleted", "w") as file:
        file.write("line1\nline2\nline3")

    assert fileHelper.deleteFile("/tmp/thisFileShouldBeDeleted")
    assert not os.path.exists("/tmp/thisFileShouldBeDeleted")
    
    # Folders should not be deleted
    try:
        os.mkdir("/tmp/thisFolderShouldNotBeDeleted")
    except FileExistsError:
        pass
    assert not fileHelper.deleteFile("/tmp/thisFolderShouldNotBeDeleted")
    assert os.path.exists("/tmp/thisFolderShouldNotBeDeleted")

def test_deleteFilesWithExtension():
    for i in range(3):
        with open(f"/tmp/thisFile{i}.shouldBeDeleted", "w") as file:
            file.write("line1\nline2\nline3")
        
        with open(f"/tmp/thisFile{i}.shouldAlsoBeDeleted", "w") as file:
            file.write("line1\nline2\nline3")

    assert fileHelper.deleteFilesWithExtension("/tmp", ".shouldBeDeleted")
    assert fileHelper.deleteFilesWithExtension("/tmp/", ".shouldAlsoBeDeleted")

    for i in range(3):
        assert not os.path.exists(f"/tmp/thisFile{i}.shouldBeDeleted")
        assert not os.path.exists(f"/tmp/thisFile{i}.shouldAlsoBeDeleted")

    # Non existent
    assert fileHelper.deleteFilesWithExtension("/tmp/thisPathDoesNotExist", ".txt")

    # Folders should not be deleted
    try:
        os.mkdir("/tmp/thisFolderShouldNot.BeDeleted")
    except FileExistsError:
        pass

    assert not fileHelper.deleteFilesWithExtension("/tmp", ".BeDeleted")
    assert os.path.exists("/tmp/thisFolderShouldNot.BeDeleted")

def test_deleteDirectory():
    try:
        os.mkdir("/tmp/ThisFolderShouldBeDeleted")
        os.mkdir("/tmp/ThisFolderShouldBeDeleted/ThisOneToo")
        os.mkdir("/tmp/ThisFolderShouldBeDeleted/SameForThis")
        os.mkdir("/tmp/ThisFolderShouldBeDeleted/SameForThis/AlsoThis")
    except FileExistsError:
        pass
    with open(f"/tmp/ThisFolderShouldBeDeleted/SameForThis/AlsoThis/ThisFileToo", "w") as file:
        file.write("line1\nline2\nline3")

    assert fileHelper.deleteDirectory("/tmp/ThisFolderShouldBeDeleted")
    assert not os.path.exists("/tmp/ThisFolderShouldBeDeleted")

    assert not fileHelper.deleteDirectory("/tmp/thisPathDoesNotExist")

def test_deleteAllInDirectory():
    try:
        os.mkdir("/tmp/ThisDirShouldStayButItsContensMustGo")
    except FileExistsError:
        pass

    for i in range(3):
        with open(f"/tmp/ThisDirShouldStayButItsContensMustGo/thisFile{i}.shouldBeDeleted", "w") as file:
            file.write("line1\nline2\nline3")
        try:
            os.mkdir(f"/tmp/ThisDirShouldStayButItsContensMustGo/Folder{i}")
        except FileExistsError:
            pass

    assert fileHelper.deleteAllInDirectory("/tmp/ThisDirShouldStayButItsContensMustGo/")
    for i in range(3):
        assert not os.path.exists(f"/tmp/ThisDirShouldStayButItsContensMustGo/thisFile{i}.shouldBeDeleted")
        assert not os.path.exists(f"/tmp/ThisDirShouldStayButItsContensMustGo/Folder{i}")

    assert fileHelper.deleteAllInDirectory("/tmp/thisPathDoesNotExist")

@mock.patch("linuxmusterLinuxclient7.fileHelper.deleteFile")
@mock.patch("linuxmusterLinuxclient7.fileHelper.deleteDirectory")
def test_deleteAllInDirectory_deletionError(mockDeleteDirectory, mockDeleteFile):
    mockDeleteDirectory.return_value = False
    mockDeleteFile.return_value = False

    try:
        os.mkdir("/tmp/ThisDirShouldStayButItsContensMustGo")
        os.mkdir("/tmp/ThisDirShouldStayButItsContensMustGo/Folder")
    except FileExistsError:
        pass

    with open("/tmp/ThisDirShouldStayButItsContensMustGo/thisFile.shouldBeDeleted", "w") as file:
        file.write("line1\nline2\nline3")

    assert not fileHelper.deleteAllInDirectory("/tmp/ThisDirShouldStayButItsContensMustGo/")