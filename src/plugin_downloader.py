import urllib.request
from urllib.error import HTTPError
import re
from web_request import doAPIRequest
from consoleoutput import oColors
from handle_config import checkConfig


def calculateFileSize(downloadFileSize):
    fileSizeDownload = int(downloadFileSize)
    fileSizeKb = fileSizeDownload / 1024
    roundedFileSize = round(fileSizeKb, 2)
    return roundedFileSize


def handleRegexPackageName(packageNameFull):
    packageNameFull2 = packageNameFull
    # trims the part of the package that has for example "[1.1 Off]" in it
    unwantedpackageName = re.search(r'(^\[+[a-zA-Z0-9\s\W*\.*\-*\+*\%*\,]*\]+)', packageNameFull)
    unwantedpackageNamematch = bool(unwantedpackageName)
    if unwantedpackageNamematch:
        unwantedpackageNameString = unwantedpackageName.group()
        packageNameFull2 = packageNameFull.replace(unwantedpackageNameString, '')
    # gets the real packagename "word1 & word2" is not supported only gets word 1
    packageName = re.search(r'([a-zA-Z]\d*)+(\s?\-*\_*[a-zA-Z]\d*\+*\-*\'*)+', packageNameFull2)
    packageNameFullString = packageName.group()
    packageNameOnly = packageNameFullString.replace(' ', '')
    return packageNameOnly


# TODO ununsed function
def getlatestVersion(packageId):
    url = f"https://api.spiget.org/v2/resources/{packageId}/versions/latest"
    response = doAPIRequest(url)
    packageVersion = response["name"]
    return packageVersion


def getVersionID(packageId, packageVersion):
    if packageVersion == None or packageVersion == 'latest':
        url = f"https://api.spiget.org/v2/resources/{packageId}/versions/latest"
        response = doAPIRequest(url)
        versionId = response["id"]
        return versionId

    url = f"https://api.spiget.org/v2/resources/{packageId}/versions?size=100&sort=-name"
    versionList = doAPIRequest(url)

    for packages in versionList:
        packageUpdate = packages["name"]
        versionId = packages["id"]
        if packageUpdate == packageVersion:
            return versionId
    return versionList[0]["id"]


def getVersionName(packageId, versionId):
    url = f"https://api.spiget.org/v2/resources/{packageId}/versions/{versionId}"
    response = doAPIRequest(url)
    versionName = response["name"]
    return versionName


def searchPackage(ressourceName):
    url = f"https://api.spiget.org/v2/search/resources/{ressourceName}?field=name"
    packageName = doAPIRequest(url)
    i = 1
    print("Index  /  Name  /  Description  /  Downloads")
    for ressource in packageName:
        pName = ressource["name"]
        pTag = ressource["tag"]
        pDownloads = ressource["downloads"]
        print(f"    [{i}] {pName} / {pTag}/ {pDownloads}")
        i = i + 1

    ressourceSelected = int(input("Select your wanted Ressource: "))
    ressourceSelected = ressourceSelected - 1
    #fileInfo = packageName[ressourceSelected]["file"]
    #packageUrl = fileInfo["url"]
    ressourceId = packageName[ressourceSelected]["id"]
    getSpecificPackage(ressourceId, checkConfig().pathToPluginFolder)


def downloadSpecificVersion(ressourceId, downloadPath, versionID='latest'):
    if versionID != 'latest':
        #url = f"https://spigotmc.org/resources/{ressourceId}/download?version={versionID}"
        print(oColors.brightRed + "Sorry but specific version downloads aren't supported because of cloudflare protection. :(" + oColors.standardWhite)
        print(oColors.brightRed + "Reverting to latest version." + oColors.standardWhite)

    url = f"https://api.spiget.org/v2/resources/{ressourceId}/download"
    #url = f"https://api.spiget.org/v2/resources/{ressourceId}/versions/latest/download" #throws 403 forbidden error

    remotefile = urllib.request.urlopen(url)
    filesize = remotefile.info()['Content-Length']
    urllib.request.urlretrieve(url, downloadPath)
    filesizeData = calculateFileSize(filesize)
    print(f"Downloadsize: {filesizeData} KB")
    print(f"File downloaded here: {downloadPath}")


def getSpecificPackage(ressourceId, downloadPath, inputPackageVersion='latest'):
    url = f"https://api.spiget.org/v2/resources/{ressourceId}"
    packageDetails = doAPIRequest(url)
    packageName = packageDetails["name"]
    packageNameNew = handleRegexPackageName(packageName)
    versionId = getVersionID(ressourceId, inputPackageVersion)
    packageVersion = getVersionName(ressourceId, versionId)
    #packageVersion = getlatestVersion(ressourceId)
    packageDownloadName = f"{packageNameNew}-{packageVersion}.jar"
    downloadPackagePath = f"{downloadPath}\\{packageDownloadName}"

    if inputPackageVersion is None or inputPackageVersion == 'latest':
        try:
            downloadSpecificVersion(ressourceId=ressourceId, downloadPath=downloadPackagePath)
        except HTTPError as err:
            print(oColors.brightRed +  f"Error: {err.code} - {err.reason}" + oColors.standardWhite)
    else:
        try:
            downloadSpecificVersion(ressourceId, downloadPackagePath, versionId)
        except HTTPError as err:
            print(oColors.brightRed +  f"Error: {err.code} - {err.reason}" + oColors.standardWhite)

# get latest update > https://api.spiget.org/v2/resources/28140/updates/latest
# this also > https://api.spiget.org/v2/resources/28140/versions/latest
# get latest download with correct name > https://api.spiget.org/v2/resources/28140/versions/latest/download cloudflare protected
# query for a plugin https://api.spiget.org/v2/search/resources/luckperms?field=name