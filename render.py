#!/usr/bin/env python

import folium
import gpxpy
from folium.plugins import TimestampedGeoJson


def get_data(fname):
    points = []
    with open(fname, 'r') as f:
        gpx = gpxpy.parse(f)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append((point.latitude, point.longitude,
                                   point.speed, point.time))
    return points


points = get_data('/tmp/track.gpx')

latitude = sum(p[0] for p in points)/len(points)
longitude = sum(p[1] for p in points)/len(points)
my_map = folium.Map(location=[latitude, longitude], zoom_start=14)

# locations = [(p[0], p[1]) for p in points]
# folium.PolyLine(locations, color="red", weight=2.5, opacity=1).add_to(my_map)

data = {
    "type": "FeatureCollection",
    "features": [{
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': [[p[1], p[0]] for p in points]
        },
        'properties': {
            'times': [p[3].timestamp() * 1000 for p in points],
        }
    }]
}

TimestampedGeoJson(data, period='PT1S').add_to(my_map)

my_map.save('test.html')
