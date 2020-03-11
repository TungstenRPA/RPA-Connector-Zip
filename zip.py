
##############################################################
############## Utility to manipulate ZIP files ###############
##############################################################
#
# This module provides tools to create, read, write, append, and list a ZIP file.
#
# Requirements:
#   - Python 3.5 or newer
#
# Author: Robert Birkenheuer
# Version: 0.1
#
##############################################################

import os
import sys
import json
import base64
import zlib
import zipfile
from zipfile import ZipFile

def list(filename):
    """
    Lists content of an archive

    Parameters:
        filename (string): path and name of the ZIP archive
    Returns:
        status (string): ok or error
        message (string): error or status message
        zipinfo (json) : zipinfo jason array
    """

    myzip = None
    infoarray = []
    status = ""
    message = ""
    filename = filename.strip()

    try:
        with ZipFile(filename) as myzip:
            infolist = myzip.infolist()
            for info in infolist:
                x = {
                "filename": info.filename,
                "filesize": info.file_size,
                "compress_size": info.compress_size,
                "modified": _formateDateTime(info.date_time)
                }
                infoarray.append(x)
            status = "ok"
            message = myzip.filename

    except FileNotFoundError as err:
        status = "error"
        message = str(err.strerror) + " " + filename
    except:
        status = "error"
        message = str(sys.exc_info()[1])

    response_text = {
        "status": status,
        "message" : message,
        "zipinfo" : json.dumps(infoarray)
    }
    return response_text


def create(filename, source, root, overwrite = 0):
    """
    Creates a ZIP archive

    Parameters:
        filename (string): path and name of the ZIP archive
        source (string): source folder or files separated by semicolon
        root (string): root folder for source
        overwrite (integer): 0 = don't overwrite existing, 1 = overwrite existing
    Returns:
        status (string): ok or error
        message (string): error or status message
    """
    myzip = None
    status = ""
    message = ""
    filecnt = 0
    filename = filename.strip()

    if overwrite == 0:
        mode = 'x'
    else:
        mode = 'w'

    list_source = source.split(";")
    try:
        for item in list_source:
            item = item.strip()
            if not os.path.exists(item):
                raise  FileNotFoundError(item)

        with ZipFile(filename, mode, zipfile.ZIP_DEFLATED) as myzip:
            for item in list_source:
                item = item.strip()
                if os.path.isfile(item):
                    archivepath = str.replace(item, root, '')
                    myzip.write(item, archivepath)
                    filecnt+=1
                else:
                    for dirpath, dirnames, filenames in os.walk(item):
                        for name in filenames:
                            #create complete filepath of file in directory
                            filePath = os.path.join(dirpath, name)
                            archivepath = str.replace(filePath, root, '')
                            myzip.write(filePath, archivepath)
                            filecnt+=1
                        for name in dirnames:
                            filePath = os.path.join(dirpath, name)
                            archivepath = str.replace(filePath, root, '')
                            myzip.write(filePath, archivepath)

            status = "ok"
            message = str(filecnt) + " files written to archive " + filename
    except FileExistsError as err:
        status = "error"
        message = str(err)
    except FileNotFoundError as err2:
        status = "error"
        message = "File not found: " + str(err2)
    except:
        status = "error"
        message = str(sys.exc_info()[1])
    
    response_text = {
        "status": status,
        "message" : message
    }
    return response_text


def extract(filename, member, path):
    """
    Extract member from archive to path

    Parameters:
        filename (string): path and name of the ZIP archive
        member (string): member file to be extracted
        path (string): target path to extract to
    Returns:
        status (string): ok or error
        message (string): error or status message
    """

    status = ""
    message = ""
    filename = filename.strip()

    try:
        with ZipFile(filename) as myzip:
            myzip.extract(member, path)
        status = "ok"
        message = "Extracted " + member + " to " + path
    except FileNotFoundError as err:
        status = "error"
        message = str(err.strerror) + " " + filename
    except:
        status = "error"
        message = str(sys.exc_info()[1])

    response_text = {
        "status": status,
        "message" : message
    }
    return response_text


def extractall(filename, path):
    """
    Extract all members from archive to path

    Parameters:
        filename (string): path and name of the ZIP archive
        path (string): target path to extract to
    Returns:
        status (string): ok or error
        message (string): error or status message
    """

    status = ""
    message = ""
    filename = filename.strip()

    try:
        with ZipFile(filename) as myzip:
            myzip.extractall(path)
        status = "ok"
        message = "Extracted " + filename + " to " + path
    except FileNotFoundError as err:
        status = "error"
        message = str(err.strerror) + " " + filename
    except:
        status = "error"
        message = str(sys.exc_info()[1])

    response_text = {
        "status": status,
        "message" : message
    }
    return response_text


def test(filename):
    """
    Read all the files in the archive and check their CRC’s and file headers.

    Parameters:
        filename (string): path and name of the ZIP archive
    Returns:
        status (string): ok or error
        message (string): error or status message
    """
    status = ""
    message = ""
    filename = filename.strip()

    try:
        with ZipFile(filename) as myzip:
            badfile = myzip.testzip()
            if (badfile):
                status = "error"
                message = badfile
            else:
                status = "ok"
                message = "Test passed for " + myzip.filename

    except FileNotFoundError as err:
        status = "error"
        message = str(err.strerror) + " " + filename
    except:
        status = "error"
        message = str(sys.exc_info()[1])

    response_text = {
        "status": status,
        "message" : message
    }
    return response_text


def _formateDateTime(dt):
    return str(dt[0])+'-'+str(dt[1])+'-'+str(dt[2])+' '+str(dt[3])+':'+str(dt[4])+':'+str(dt[5])


# For testing purpose if the script is called via shell
if __name__ == '__main__':
    #print(list('c:/temp/Demo.zip'))
    #print(create('c:/temp/connector.zip', 'c:/temp/kiaalap-master', 'c:/temp', 0))
    #print(create('c:/temp/connector.zip', 'c:/temp/Demo3.pdf;c:/temp/Demo4.pdf;c:/temp/Demo5.pdf;c:/temp/fatturapo', 'c:/temp', 1))
    #print(extractall('C:/temp/webzip/tester/backup.zip', 'c:/temp/backup_extracted'))
    #print(extract('C:/temp/webzip/tester/backup.zip', 'version.txt', 'c:/temp/backup_extracted_member'))
    print(test('C:/temp/webzip/tester/backup.zip'))