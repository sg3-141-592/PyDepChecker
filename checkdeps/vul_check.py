from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pprint import pprint
import logging
import json
import os
from os import listdir
from os.path import isfile, join

def getVul(package, version):

    PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),'insecure_full.json')

    logging.info(PATH)

    with open(PATH) as json_file:
        results = []
        vulnerabilities = json.load(json_file)
        # Try and find a match
        if package in vulnerabilities:
            for vul in vulnerabilities[package]:
                # See if the version applies
                for spec in vul['specs']:
                    if version in SpecifierSet(spec):
                        details = {'cve' : 'undefined', 'details' : vul['advisory']}
                        if vul['cve']:
                            details['cve'] = vul['cve']
                        results.append(details)
        return results