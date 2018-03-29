#!/usr/bin/python3

import csv
import xml.etree.ElementTree as ET

def main():
    parseXML('new_york_sample.xml')

def parseXML(xmlfile):
    print(xmlfile)
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    print(root)

    id = 1
    intersections = []

    for i in root.findall('./node'):
        j = i.find('tag')
        if j is not None and j.attrib['v'] == 'traffic_signals':
            k = []
            k.append(id)
            k.append(i.attrib['lat'])
            k.append(i.attrib['lon'])
            intersections.append(k)
            id = id + 1

    headers = ['id', 'latitude', 'longitude']
    with open('NYC_Intersetions.csv', 'w') as output_file:
        writer = csv.writer(output_file, dialect='excel')
        writer.writerow(headers)
        writer.writerows(intersections)


if __name__ == '__main__':
    main()