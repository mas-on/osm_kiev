# TODO solve Lesson 6 problems: count tags, check subtags for validity, count unique users, improve street names, prepare for database

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import time


def count_tags(filename):
    tags = defaultdict(int)
    for _,el in ET.iterparse(filename):
        tags[el.tag] += 1
    return tags


if __name__ == "__main__":
    fname = 'D:\Projects\OpenStreetMap\Kyiv\map'
    start = time.time()

    pprint.pprint(count_tags(fname).items())
    end = time.time()
    print "finished in %d seconds!" % (end-start)