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
lower_upper = re.compile(r'^([a-zA-Z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
letters = re.compile(r'^([^\d|\W])*$',flags=re.UNICODE)
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_re = re.compile(r'\b\S+\.?$', flags=re.IGNORECASE|re.UNICODE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", u"площа", u"провулок", u"узвіз", u"проспект", u"вулиця",
            u"алея", u"шосе", u"переулок", u"проїзд", u"бульвар", u"дорога", u"набережна"]

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


def key_type(element, keys, strangekeys):
    if element.tag == "tag":
        k = element.attrib['k']

        for char in k:
            if problemchars.match(char) != None:
                keys['problemchars'] += 1
                strangekeys.append(('problemchars',k,element.attrib['v']))
                return

        if letters.match(k) != None:
            if lower.match(k) != None:
                keys['lower'] += 1
            elif lower_upper.match(k) != None:
                keys['lower_upper'] += 1
            else: # non-latin letters
                keys['nonlatin'] += 1
                strangekeys.append(('nonlatin',k,element.attrib['v']))
        elif lower_colon.match(k) != None:
            keys['lower_colon'] += 1
        else:
            keys['other'] += 1

    return

#check usertags for validity
def check_keys(filename):
    countkeys = {"lower": 0, "lower_upper" : 0, "lower_colon": 0, "nonlatin" : 0, "problemchars": 0, "other": 0}
    strangekeys = []
    for _, element in ET.iterparse(filename):
        key_type(element, countkeys, strangekeys)
    return countkeys, strangekeys


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


def get_stats(filename):
    tag_stats = defaultdict(int) #tags statistics - which data we can expect to have in the map
    countkeys = {"lower": 0, "lower_upper" : 0, "lower_colon": 0, "nonlatin" : 0, "problemchars": 0, "other": 0}
    strangekeys = []
    users = set()
    street_types = defaultdict(set)
    for event, el in ET.iterparse(filename,events=("start",)):
        tag_stats[el.tag] += 1
        key_type(el, countkeys, strangekeys) #check usertags for validity
        if 'uid' in el.attrib:
            users.add(el.attrib['uid'])
        if event == "start" and (el.tag == "node" or el.tag == "way"):
            for tag in el.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return tag_stats, {'countkeys' : countkeys, 'strangekeys' : strangekeys}, users, street_types


def save_stats(filename, stats):
    import csv

    tags_stats, keys_stats, unq_users, street_types = stats
    print street_types
    with open(filename, 'wb') as f:
        w = csv.writer(f)

        w.writerow(('Unique users quantity: {}'.format(len(unq_users)),))
        w.writerow('')

        w.writerow(('Tags Statistics:',))
        w.writerow(tags_stats.keys())
        w.writerow([val for key, val in tags_stats.items()])
        w.writerow('')

        w.writerow(('Keys Statistics:',))
        stat = keys_stats['countkeys']
        w.writerow(stat.keys())
        w.writerow([stat[key] for key in stat])
        w.writerow('')

        w.writerow(('Strange Keys:',))
        w.writerow(('Type','Key','Value'))
        for row in keys_stats['strangekeys']:
            w.writerow([el.encode('utf-8') for el in row])
        w.writerow('')

        w.writerow(('Unexpected Street Types: {}'.format(len(street_types)),))
        w.writerow(('Found type','Value example'))
        for key, val in street_types.items():
            w.writerow((key.encode('utf-8'),tuple(val)[0].encode('utf-8')))
        w.writerow('')


if __name__ == "__main__":
    with open("filename.txt", "rb") as f:
        fmap = f.read()

        start = time.time()

        statfile = "statistics.csv"
        save_stats(statfile, get_stats(fmap))

        end = time.time()
        print "finished in %d seconds!" % (end-start)