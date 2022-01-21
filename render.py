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


points = get_data('track.gpx')
points2 = get_data('track2.gpx')

latitude = sum(p[0] for p in points)/len(points)
longitude = sum(p[1] for p in points)/len(points)
my_map = folium.Map(location=[latitude, longitude], zoom_start=14)

# locations = [(p[0], p[1]) for p in points]
# folium.PolyLine(locations, color="red", weight=2.5, opacity=1).add_to(my_map)

data = {
    "type": "FeatureCollection",
    "features": []
}


def add_track(points, dt):
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': [[p[1], p[0]] for p in points]
        },
        'properties': {
            'times': [(p[3].timestamp() + dt) * 1000 for p in points],
            'style': {
                'color': "#f00",
                'opacity': 0.5,
            },
        }
    }
    data['features'].append(feature)


dt = (points[0][3] - points2[0][3]).total_seconds()

add_track(points, 0)
add_track(points2, dt)

TimestampedGeoJson(data, period='PT5S', transition_time=50).add_to(my_map)

my_map.save('test.html')
