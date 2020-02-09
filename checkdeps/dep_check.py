from pprint import pprint
import requests
import json
import re


def traverseDeps(package, version=None, tree=None, fullTree=None):

    url = None
    if version:
        url = "https://pypi.org/pypi/{name}/{version}/json".format(
            name=package, version=version
        )
    else:
        url = "https://pypi.org/pypi/{name}/json".format(name=package)

    try:
        jsonData = requests.get(url).json()
    except:
        print("Error accessing {}".format(url))
        return None

    # Append license information to the tree
    tree["data"]["license"] = jsonData["info"]["license"]
    tree["data"]["version"] = jsonData["info"]["version"]

    # Get dependencies
    dependencies = jsonData["info"]["requires_dist"]

    if dependencies:
        for dep in dependencies:
            if decodeVersion(dep) != (None, None):
                (pack, vers) = decodeVersion(dep)
                # Check for circular dependencies, skip if there are any
                if not iterateDict(fullTree, pack):
                    newEntry = {"name": pack, "children": [], "data": {}}
                    tree["children"].append(newEntry)
                    traverseDeps(pack, tree=newEntry, fullTree=fullTree)

    return tree


def decodeVersion(package):
    # Check if dependency is an extra
    extraMatch = re.compile("^.*\(.*\).*;.*extra")
    reCheck = extraMatch.match(package)
    if reCheck:
        return (None, None)
    # Check if dependency is in format python-dateutil (>=2.6.1)
    versionMatch = re.compile("^(?P<package>\S*?) \((?P<version>.*?)\).*")
    reCheck = versionMatch.match(package)
    if reCheck:
        return (reCheck.group("package"), reCheck.group("version"))
    # Check if depdency is in format
    semiColonMatch = re.compile(r"(?P<package>^\S*);")
    reCheck = semiColonMatch.match(package)
    if reCheck:
        return (reCheck.group("package"), None)
    # Check if dependency is in format python-dateutil
    packageNameMatch = re.compile(r"(?P<package>^\S*)")
    reCheck = packageNameMatch.match(package)
    if reCheck:
        return (reCheck.group("package"), None)
    # Check if dependency is in format
    packageSemiColonMatch = re.compile(r"^(?P<package>^\S*) ;")
    reCheck = packageSemiColonMatch.match(package)
    if reCheck:
        return (reCheck.group("package"), None)
    # No version number in this line
    print("{} is not decodeable".format(package))
    return (package, None)


# Iterate through a nested dict structure to find a match
def iterateDict(d, target):
    if d["name"] == target:
        return True
    for child in d["children"]:
        if child["name"] == target:
            return True
        if len(child["children"]) > 0:
            if iterateDict(child, target):
                return True
    return False


def getDeps(package, version=None):
    tree = {"name": package, "children": [], "data": {}}
    return traverseDeps(package=package, version=version, tree=tree, fullTree=tree)
