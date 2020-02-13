from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pprint import pprint
import requests
import re

from .vul_check import getVul


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


def traverseDeps(package, version=None, tree=None, fullTree=None, summary=None):

    jsonData = getPypiData(package, version)

    # Append license information to the tree
    tree["data"]["license"] = jsonData["info"]["license"]
    tree["data"]["version"] = jsonData["info"]["version"]
    tree["data"]["url"] = jsonData["info"]["release_url"]
    tree["data"]["vulnerabilities"] = getVul(package, version)

    # Update summary metrics
    summary["licenses"].add(jsonData["info"]["license"])

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
                    traverseDeps(pack, tree=newEntry, fullTree=fullTree, summary=summary)

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
        # print("Skipping ", req.name, " due to ", req.marker)
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
    if isinstance(d, list):
        for child in d:
            if iterateDict(child, target):
                return True
            else:
                return False
    else:
        if d["name"] == target:
            return True
        for child in d["children"]:
            if child["name"] == target:
                return True
            if len(child["children"]) > 0:
                if iterateDict(child, target):
                    return True
        return False

def getDep(package, fullTree, summary=None):
    """
    Get single dependency
    """
    (pack, vers) = decodeVersion(package)
    tree = {"name": pack, "children": [], "data": {}}
    fullTree.append(traverseDeps(package=pack, version=vers, tree=tree, fullTree=fullTree, summary=summary))

def getDeps(packages):
    """
    Get a newline separated list of dependencies
    """
    fullTree = []
    summary = { 'licenses' : set() }
    for package in packages.split('\n'):
        if package != '':
            getDep(package, fullTree, summary=summary)
    return {'data': fullTree, 'summary': summary}
