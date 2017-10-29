#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This python program saves test XMLs from denon receiver to current directory.

Usage: python denon_receiver_xml.py --host 192.168.0.250 --prefix AVR-X4100W

:copyright: (c) 2017 by Oliver Goetz.
:license: MIT, see LICENSE for more details.
"""
import argparse
from io import BytesIO
import requests
import xml.etree.ElementTree as ET
from collections import namedtuple

XML = namedtuple("XML", ["type", "path", "filename"])

SAVED_XML = [XML("post", "/goform/AppCommand.xml", "AppCommand.xml"),
             XML("get", "/goform/Deviceinfo.xml", "Deviceinfo.xml"),
             XML("get", "/goform/formMainZone_MainZoneXmlStatus.xml",
                 "formMainZone_MainZoneXmlStatus.xml"),
             XML("get", "/goform/formMainZone_MainZoneXml.xml",
                 "formMainZone_MainZoneXml.xml"),
             XML("get", "/goform/formNetAudio_StatusXml.xml",
                 "formNetAudio_StatusXml.xml"),
             XML("get", "/goform/formTuner_TunerXml.xml",
                 "formTuner_TunerXml.xml"),
             XML("get", "/goform/formTuner_HdXml.xml",
                 "formTuner_HdXml.xml"),
             XML("get", "/goform/formZone2_Zone2XmlStatus.xml",
                 "formZone2_Zone2XmlStatus.xml"),
             XML("get", "/goform/formZone3_Zone3XmlStatus.xml",
                 "formZone3_Zone3XmlStatus.xml")]


def http_post(host, path, filename):
    root = ET.Element("tx")
    item = ET.Element("cmd")
    item.set("id", "1")
    item.text = "GetRenameSource"
    root.append(item)
    item = ET.Element("cmd")
    item.set("id", "1")
    item.text = "GetDeletedSource"
    root.append(item)
    xml = BytesIO()
    tree = ET.ElementTree(root)
    tree.write(xml, encoding='utf-8', xml_declaration=True)
    try:
        r = requests.post(
            "http://{host}/{path}".format(host=host, path=path),
            data=xml.getvalue())
    except requests.exceptions.ConnectionError:
        print("ConnectionError retrieving data from host {} path {}".format(
            host, path))
        xml.close()
        return
    except requests.exceptions.Timeout:
        print("Timeout retrieving data from host {} path {}".format(
            host, path))
        xml.close()
        return
    xml.close()
    print("HTTP Status Code of {}: {}".format(path, r.status_code))
    with open("./{}".format(filename), "wb") as file:
        file.write(r.content)


def http_get(host, path, filename):
    try:
        r = requests.get(
            "http://{host}/{path}".format(host=host, path=path))
    except requests.exceptions.ConnectionError:
        print("ConnectionError retrieving data from host {} path {}".format(
            host, path))
        return
    except requests.exceptions.Timeout:
        print("Timeout retrieving data from host {} path {}".format(
            host, path))
        return
    print("HTTP Status Code of {}: {}".format(path, r.status_code))
    with open("./{}".format(filename), "wb") as file:
        file.write(r.content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str,
                        default='192.168.0.250',
                        help='host of Denon AVR receiver')
    parser.add_argument('--prefix', type=str,
                        default='AVR',
                        help='prefix of filenames to be saved')
    args = parser.parse_args()

    for entry in SAVED_XML:
        if entry.type == "post":
            http_post(args.host, entry.path, "{}-{}".format(
                args.prefix, entry.filename))
        elif entry.type == "get":
            http_get(args.host, entry.path, "{}-{}".format(
                args.prefix, entry.filename))
        else:
            print("wrong type, only \"get\" and \"post\" are allowed")
