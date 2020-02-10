from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pprint import pprint
import requests
import re


def getPypiData(package, version=None):

    url = None
    if version:
        url = "https://pypi.org/pypi/{name}/{version}/json".format(
            name=package, version=version
        )
    else:
        url = "https://pypi.org/pypi/{name}/json".format(name=package)

    try:
        jsonData = requests.get(url).json()
        return jsonData
    except:
        print("Error accessing {}".format(url))
        return None


def traverseDeps(package, version=None, tree=None, fullTree=None):

    jsonData = getPypiData(package, version)

    # Append license information to the tree
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
    try:
        req = Requirement(package)
    except:
        print("Invalid requirement: ", package)
        return None, None
    # Check if extras are specified
    if req.marker:
        # TODO: Implement proper support for handling these markers using the req.marker.evaluate()
        # We might have to let people specify their Python environment on the page
        print("Skipping ", req.name, " due to ", req.marker)
        return None, None
    # Check if a version is specified
    if req.specifier:
        # Take the list of releases from PyPi and find the newest compatible release
        depData = getPypiData(req.name)
        compatibleVersions = []
        for release in depData["releases"]:
            if release in req.specifier:
                compatibleVersions.append(Version(release))
        return req.name, max(compatibleVersions)
    return req.name, None

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
