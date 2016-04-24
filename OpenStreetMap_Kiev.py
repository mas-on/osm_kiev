#!/usr/bin/python
# -*- coding: utf-8 -*-
# TODO solve Lesson 6 problems: improve street names, prepare for database

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import time
import json
import re
import codecs
#from transliterate import translit, get_available_language_codes
# TODO this is test row

lower = re.compile(r'^([a-z]|_)*$')
lower_upper = re.compile(r'^([a-zA-Z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
letters = re.compile(r'^([^\d|\W])*$',flags=re.UNICODE)
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_after_re = re.compile(r'\b\S+\.?$', flags=re.IGNORECASE | re.UNICODE)
street_type_before_re = re.compile(r'^\S+[\.|\s]', flags=re.IGNORECASE | re.UNICODE)

expected = [u"площа", u"провулок", u"узвіз", u"проспект", u"вулиця",
            u"алея", u"шосе", u"переулок", u"проїзд", u"бульвар", u"дорога", u"набережна", u"улица", u"шлях"]

mapping = { u"вул." : u"вулиця",
            u"ул." : u"улица"
            }



CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

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
    m = street_type_after_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type.lower() not in expected:
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

class Address:
    housenumber =[]
    streetname = []

    def __init__(self, dirty_streetname, dirty_housenumber):
        # TODO add address cleaning logic
        housenumber =


def change_streettype_place(name):
    streettype = street_type_before_re.search(name)
    if streettype != None:
        streettype = streettype.group().rstrip()
        if streettype in mapping:
            streettype = mapping[streettype]
        if streettype.lower() in expected:
            return name.replace(streettype,'').lstrip()+' '+streettype

    return name


def add_streettype_to(name):
    if len(name.split()) == 1:
        if name[-2:] == u"ая":
            return  name + u" улица"
        elif name[-1] in (u"а", u"ї") or name[-2:] == u"ик":
            return  name + u" вулиця"
    return name

# convert "15/4","Хрещатик/Заньковецкої"
# to   addr["housenumber"]="15", addr["street"]="Хрещатик вулиця",
#      addr["housenumber2"]="4"addr["street2"]="Заньковецкої вулиця"
def shape_address(node, house, street):
    streets = street.split('/')
    for i in range(len(streets)):
        node["street{}".format('' if i == 0 else i+1)] = add_streettype_to(streets[i])
    if len(streets) > 1: # keep in mind houses with a double number at one street
        houses = house.split('/')
        for i in range(len(houses)):
            node["housenumber{}".format('' if i == 0 else i+1)] = houses[i]


# TODO get translit values, divide the addr tag with a house number into addr:street and addr:housenumber
def restore_translit(name):
    if lower.match(name) == None:
        return name



def update_name(name, mapping):
    short = street_type_after_re.search(name).group()
    full = mapping[short]
    return name.replace(short,full)

#endregion check street names section


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # node['type'] = element.tag
        # node['created'] = {}
        # node['pos'] = []
        node = {'type' : element.tag, 'created' : {}, 'pos' : [] }
        for attr in element.attrib:
            if attr in CREATED:
                node['created'][attr] = element.attrib[attr]
            elif attr not in ('lat','lon'):
                node[attr] = element.attrib[attr]
        if 'lat' in element.attrib:
            node['pos'].append(float(element.attrib['lat']))
            node['pos'].append(float(element.attrib['lon']))
        house = street = ''
        for tag in element.iter('tag'):
            k = tag.attrib['k']

            if problemchars.search(k) == None:
                if k.startswith('addr:'):
                    if 'address' not in node:
                        node['address'] = {}
                    addr_key = k.split(':')
                    if len(addr_key) == 2:
                        addr_subkey = addr_key[1]
                        if addr_subkey == "housenumber":
                            house = tag.attrib['v']
                        elif addr_subkey == "street":
                            street = tag.attrib['v']
                        else:
                            node['address'][addr_subkey] = tag.attrib['v']
                else:
                    node[k] = tag.attrib['v']
        shape_address(node['address'], house, street)
        if element.tag == "way":
            node_refs = []
            for nd in element.iter('nd'):
                node_refs.append(nd.attrib['ref'])
            if len(node_refs)>0:
                node['node_refs'] = node_refs

        return node
    else:
        return None


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


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
                    audit_street_type(street_types, add_streettype_to(change_streettype_place(tag.attrib['v'])))

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

    #name = u"Урлівська"
    #print add_streettype_to(change_streettype_place(name))

    # address = {}
    # shape_address(address,'15/4',u'Хрещатик/Заньковецкої')
    # for el in address:
    #     print el, address[el]


    #print translit("zhylianskaya", 'ru')

    from mytranslit import translit2ru, translit2uk
    print translit2ru("zhylianskaya")
    print translit2uk("Gogolevska")
    # TODO заменить гоголевску страду на Гоголівська вулиця
"""
    with open("filename.txt", "rb") as f:
        fmap = f.read()

        start = time.time()

        statfile = "statistics.csv"
        save_stats(statfile, get_stats(fmap))



        end = time.time()
        print "finished in %d seconds!" % (end-start)
"""