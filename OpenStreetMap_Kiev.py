#!/usr/bin/python
# -*- coding: utf-8 -*-
# TODO solve Lesson 6 problems: improve street names, prepare for database

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import time
import json
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]

mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Rd." : "Road"
            }

def count_tags(filename):
    tags = defaultdict(int)
    for _,el in ET.iterparse(filename):
        tags[el.tag] += 1
    return tags


def get_tags_stats(fmap, fstat):
    with open(fstat,"wb") as fstat:
        data = count_tags(fmap).items()
        json.dump(data, fstat)
        pprint.pprint(data)


def key_type(element, keys):
    if element.tag == "tag":
        k = element.attrib['k']
        if lower.match(k) != None:
            keys['lower'] += 1
        elif lower_colon.match(k) != None:
            keys['lower_colon'] += 1
        else:
            for char in k:
                if problemchars.match(char) != None:
                    keys['problemchars'] += 1
                    print "problem key=", k, " value=", element.attrib['v']
                    break
            else:
                keys['other'] += 1
                print k

    return keys


def check_keys(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys


def get_unique_users(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if 'uid' in element.attrib:
            users.add(element.attrib['uid'])
    return users

#region check street names section
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


def update_name(name, mapping):
    short = street_type_re.search(name).group()
    full = mapping[short]
    return name.replace(short,full)

#endregion check street names section


if __name__ == "__main__":
    with open("filename.txt", "rb") as f:
        fmap = f.read()

        start = time.time()
        #tags statistics - which data we can expect to have in the map
        #get_tags_stats(fmap, "tags_statistics.txt")

        #check subtags for validity
        #pprint.pprint(check_keys(fmap))

        #count unique users
        #pprint.pprint(len(get_unique_users(fmap)))

        #audit street names
        #pprint.pprint(audit(fmap))
        #TODO support utf-8 street names
        m = street_type_re.search("jphn street")
        print m
        end = time.time()
        print "finished in %d seconds!" % (end-start)