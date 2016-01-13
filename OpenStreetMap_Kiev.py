# TODO solve Lesson 6 problems: check subtags for validity, count unique users, improve street names, prepare for database

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import time
import json
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

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
                    print k
                    break
            else:
                keys['other'] += 1

    return keys


def check_keys(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys


if __name__ == "__main__":
    with open("filename.txt", "rb") as f:
        fmap = f.read()

        start = time.time()
        #get_tags_stats(fmap, "tag_statistics.txt")
        pprint.pprint(check_keys(fmap))
        end = time.time()
        print "finished in %d seconds!" % (end-start)