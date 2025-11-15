import os, shutil
from linuxmusterLinuxclient7 import logging

def removeLinesInFileContainingString(filePath, forbiddenStrings):
    """
    Remove all lines containing a given string form a file.

    :param filePath: The path to the file
    :type filePath: str
    :param forbiddenStrings: The string to search for
    :type forbiddenStrings: str or list[str]
    :return: True on success, False otherwise
    :rtype: bool
    """
    if not isinstance(forbiddenStrings, list):
        forbiddenStrings = [forbiddenStrings]
    
    try:
        with open(filePath, "r") as originalFile:
            originalContents = originalFile.read()
    except Exception as e:
        logging.exception(e)
        logging.warning("Could not read contents of original file")
        return False

    newContents = ""
    for line in originalContents.split("\n"):
        lineIsClean = True
        for forbiddenString in forbiddenStrings:
            lineIsClean = lineIsClean and not forbiddenString in line
            
        if lineIsClean :
            newContents += line + "\n"

    try:
        with open(filePath, "w") as originalFile:
            originalFile.write(newContents)
    except Exception as e:    
        logging.exception(e)
        logging.warning("Could not write new contents to original file")
        return False

    return True

def deleteFile(filePath):
    """
    Delete a file

    :param filePath: The path of the file
    :type filePath: str
    :return: True on success or if the file does not exist, False otherwise
    :rtype: bool
    """
    try:
        if os.path.exists(filePath):
            os.remove(filePath)
        return True
    except Exception as e:
        logging.error("Failed!")
        logging.exception(e)
        return False

def deleteFilesWithExtension(directory, extension):
    """
    Delete all files with a given extension in a given directory.

    :param directory: The path of the directory
    :type directory: str
    :param extension: The file extension
    :type extension: str
    :return: True on success or if the path does not exist, False otherwise
    :rtype: bool
    """
    if directory.endswith("/"):
        directory = directory[:-1]
        
    if not os.path.exists(directory):
        return True

    existingFiles=os.listdir(directory)

    for file in existingFiles:
        if file.endswith(extension):
            logging.info(f"* Deleting {file}")
            if not deleteFile(f"{directory}/{file}"):
                logging.error("Failed!")
                return False

    return True

def deleteDirectory(directory):
    """
    Recoursively delete a directory.

    :param directory: The path of the directory
    :type directory: bool
    :return: True on success, False otherwise
    :rtype: bool
    """
    try:
        shutil.rmtree(directory)
    except:
        return False
    return True

def deleteAllInDirectory(directory):
    """
    Delete all files and folders in a given directory

    :param directory: The path of the directory
    :type directory: str
    :return: True on success or if the directory does not exist, False otherwise
    :rtype: bool
    """    

    if directory.endswith("/"):
        directory = directory[:-1]
        
    if not os.path.exists(directory):
        return True

    existingFiles=os.listdir(directory)
    for file in existingFiles:
        fullFilePath = f"{directory}/{file}"
        if os.path.isdir(fullFilePath):
            rc = deleteDirectory(fullFilePath)
        else:
            rc = deleteFile(fullFilePath)
        if not rc:
            logging.error("Failed!")
            return False

    return True