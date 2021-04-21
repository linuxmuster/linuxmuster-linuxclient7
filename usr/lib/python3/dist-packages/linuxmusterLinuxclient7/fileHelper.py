import os, shutil
from linuxmusterLinuxclient7 import logging

def removeLinesInFileContainingString(filePath, forbiddenStrings):
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
    try:
        if os.path.exists(filePath):
            os.unlink(filePath)
        return True
    except Exception as e:
        logging.error("Failed!")
        logging.exception(e)
        return False

def deleteFilesWithExtension(directory, extension):
    if directory.endswith("/"):
        directory = directory[:-1]
        
    existingFiles=os.listdir(directory)

    for file in existingFiles:
        if file.endswith(extension):
            logging.info("* Deleting {}".format(file))
            if not deleteFile("{}/{}".format(directory, file)):
                logging.error("Failed!")
                return False

    return True

def deleteDirectory(directory):
    try:
        shutil.rmtree(directory)
    except:
        return False
    return True