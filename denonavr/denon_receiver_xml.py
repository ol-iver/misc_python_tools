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

XML = namedtuple("XML", ["port", "type", "path", "tags", "filename"])

SAVED_XML = [XML("80", "post", "/goform/AppCommand.xml",
                 ["GetRenameSource", "GetDeletedSource"],
                 "AppCommand"),
             XML("80", "post", "/goform/AppCommand.xml",
                 ["GetAllZonePowerStatus", "GetAllZoneSource",
                  "GetAllZoneVolume", "GetAllZoneMuteStatus"],
                 "AppCommand-2016"),
             XML("80", "get", "/goform/Deviceinfo.xml", [], "Deviceinfo.xml"),
             XML("80", "get", "/goform/formMainZone_MainZoneXmlStatus.xml",
                 [], "formMainZone_MainZoneXmlStatus"),
             XML("80", "get", "/goform/formMainZone_MainZoneXml.xml",
                 [], "formMainZone_MainZoneXml"),
             XML("80", "get", "/goform/formNetAudio_StatusXml.xml",
                 [], "formNetAudio_StatusXml"),
             XML("80", "get", "/goform/formTuner_TunerXml.xml",
                 [], "formTuner_TunerXml"),
             XML("80", "get", "/goform/formTuner_HdXml.xml",
                 [], "formTuner_HdXml"),
             XML("80", "get", "/goform/formZone2_Zone2XmlStatus.xml",
                 [], "formZone2_Zone2XmlStatus"),
             XML("80", "get", "/goform/formZone3_Zone3XmlStatus.xml",
                 [], "formZone3_Zone3XmlStatus"),
             XML("8080", "post", "/goform/AppCommand.xml",
                 ["GetRenameSource", "GetDeletedSource"],
                 "AppCommand"),
             XML("8080", "post", "/goform/AppCommand.xml",
                 ["GetAllZonePowerStatus", "GetAllZoneSource",
                  "GetAllZoneVolume", "GetAllZoneMuteStatus"],
                 "AppCommand-2016"),
             XML("8080", "get", "/goform/Deviceinfo.xml", [],
                 "Deviceinfo.xml"),
             XML("8080", "get", "/goform/formMainZone_MainZoneXmlStatus.xml",
                 [], "formMainZone_MainZoneXmlStatus"),
             XML("8080", "get", "/goform/formMainZone_MainZoneXml.xml",
                 [], "formMainZone_MainZoneXml"),
             XML("8080", "get", "/goform/formNetAudio_StatusXml.xml",
                 [], "formNetAudio_StatusXml"),
             XML("8080", "get", "/goform/formTuner_TunerXml.xml",
                 [], "formTuner_TunerXml"),
             XML("8080", "get", "/goform/formTuner_HdXml.xml",
                 [], "formTuner_HdXml"),
             XML("8080", "get", "/goform/formZone2_Zone2XmlStatus.xml",
                 [], "formZone2_Zone2XmlStatus"),
             XML("8080", "get", "/goform/formZone3_Zone3XmlStatus.xml",
                 [], "formZone3_Zone3XmlStatus")]


def create_post_body(attribute_list):
    # Prepare POST XML body for AppCommand.xml
    post_root = ET.Element("tx")

    for attribute in attribute_list:
        # Append tags for each attribute
        item = ET.Element("cmd")
        item.set("id", "1")
        item.text = attribute
        post_root.append(item)

    # Buffer XML body as binary IO
    body = BytesIO()
    post_tree = ET.ElementTree(post_root)
    post_tree.write(body, encoding="utf-8", xml_declaration=True)

    return body.getvalue()


def http_post(host, port, path, tags, filename):

    filename = filename + "-" + str(port)

    data = create_post_body(tags)

    try:
        r = requests.post(
            "http://{host}:{port}/{path}".format(
                host=host, port=port, path=path), data=data)
    except requests.exceptions.ConnectionError:
        print("ConnectionError retrieving data from host {} port {} \
                path {}".format(host, port, path))
        filename = filename + "-ConnectionError.xml"
        with open("./{}".format(filename), "wb") as file:
            file.write("".encode())
    except requests.exceptions.Timeout:
        print("Timeout retrieving data from host {} port {} path {}".format(
            host, port, path))
        filename = filename + "-Timeout.xml"
        with open("./{}".format(filename), "wb") as file:
            file.write("".encode())
    else:
        print("HTTP Status Code of {}: {}".format(path, r.status_code))
        filename = filename + "-" + str(r.status_code) + ".xml"
        with open("./{}".format(filename), "wb") as file:
            file.write(r.content)


def http_get(host, port, path, filename):

    filename = filename + "-" + str(port)

    try:
        r = requests.get(
            "http://{host}:{port}/{path}".format(
                host=host, port=port, path=path))
    except requests.exceptions.ConnectionError:
        print("ConnectionError retrieving data from host {} path {}".format(
            host, path))
        filename = filename + "-ConnectionError.xml"
        with open("./{}".format(filename), "wb") as file:
            file.write("".encode())
    except requests.exceptions.Timeout:
        print("Timeout retrieving data from host {} path {}".format(
            host, path))
        filename = filename + "-Timeout.xml"
        with open("./{}".format(filename), "wb") as file:
            file.write("".encode())
    else:
        print("HTTP Status Code of {}: {}".format(path, r.status_code))
        filename = filename + "-" + str(r.status_code) + ".xml"
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
            http_post(args.host, entry.port, entry.path, entry.tags,
                      "{}-{}".format(args.prefix, entry.filename))
        elif entry.type == "get":
            http_get(args.host, entry.port, entry.path, "{}-{}".format(
                args.prefix, entry.filename))
        else:
            print("wrong type, only \"get\" and \"post\" are allowed")
