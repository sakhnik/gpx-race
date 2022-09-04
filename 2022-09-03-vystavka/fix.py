#!/usr/bin/env python

# Remove the pause around 10am

from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
tree = ET.parse('course.gpx')
root = tree.getroot()

for pt in root[1][0]:
    d = pt.find('{http://www.topografix.com/GPX/1/1}time')
    dt = datetime.strptime(d.text, "%Y-%m-%dT%H:%M:%SZ")
    if dt.time().hour >= 10:
        dt -= timedelta(0, 7*60 + 10)
    d.text = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

tree.write('course2.gpx')
