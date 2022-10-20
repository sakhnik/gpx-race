import folium
from folium.plugins import TimestampedGeoJson
import exif
from PIL import Image
import io
import base64
import pandas as pd


class FinalMap:

    def __init__(self, tracks, anchors, pictures):
        location = tracks.center if tracks else None
        self.m = folium.Map(location=location, zoom_start=14)
        self.colors = ['red', 'blue', 'green', 'cyan', 'magenta', 'brown',
                       'darkcyan']

        if anchors:
            img = folium.raster_layers.ImageOverlay(
                name="Orienteering map",
                image=anchors.get_aligned_url(),
                bounds=anchors.get_bounds(),
                opacity=1,
                interactive=False,
                cross_origin=False,
                zindex=1,
            )
            img.add_to(self.m)

        data = {
            "type": "FeatureCollection",
            "features": []
        }

        def add_track(name, color, points, dt):
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [[p[1], p[0]] for p in points]
                },
                'properties': {
                    'times': [(p[3].timestamp() + dt) * 1000 for p in points],
                    'icon': 'circle',
                    'popup': name,
                    'style': {
                        'color': color,
                        'opacity': 0.75,
                    },
                    'iconStyle': {
                        'color': color
                    }
                }
            }
            data['features'].append(feature)

        if tracks:
            for i, points in enumerate(tracks.points):
                dt = (tracks.points[0][0][3] - points[0][3]).total_seconds()
                add_track(tracks.names[i], self.colors[i], points, dt)

            TimestampedGeoJson(data,
                               period='PT1S',
                               transition_time=50,
                               duration='PT1M') \
                .add_to(self.m)
            folium.LayerControl().add_to(self.m)
            self.create_result_table(tracks)

        # Mark the pictures on the map
        def get_pic_coords(pic_bytes):
            def to_dec(coords, ref):
                decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
                if ref == "S" or ref == "W":
                    return -decimal_degrees
                return decimal_degrees
            img = exif.Image(pic_bytes)
            coords = [to_dec(img.gps_latitude, img.gps_latitude_ref),
                      to_dec(img.gps_longitude, img.gps_longitude_ref)]
            return coords

        for pic in pictures:
            coords = get_pic_coords(pic)
            pic_f = Image.open(io.BytesIO(pic))
            width, height = pic_f.size
            encoded = base64.b64encode(pic)
            jpg = """
                <object data="data:image/jpg;base64,{}" width="{}" height="{}
                    type="image/jpg">
                </object>""".format
            iframe = folium.IFrame(jpg(encoded.decode('UTF-8'), width, height),
                                   width=width*1.1, height=height*1.1)
            popup = folium.Popup(iframe, parse_html=True, max_width=1500)
            folium.Marker(
                coords,
                icon=folium.Icon(color='red', icon='image', prefix='fa'),
                popup=popup).add_to(self.m)

    def create_result_table(self, tracks):
        if not tracks:
            return

        results = {
            "Runner": [tracks.names[idx] for idx, _ in tracks.results],
            "Color": [self.colors[idx] for idx, _ in tracks.results],
            "Time": [f"{time}" for _, time in tracks.results]
        }
        dat = pd.DataFrame(results,
                           index=[i + 1 for i, _ in enumerate(tracks.results)])
        dat = dat.style \
            .applymap(lambda c: f"background-color: {c};", subset="Color")
        style = " ".join(f"table{i}" for i in ("", "-striped", "-hover",
                                               "-condensed", "-responsive"))
        dat = dat.set_table_attributes(f'class="{style}"')
        html = dat.to_html()

        pos = tracks.points[0][0]
        popup = folium.Popup(html)
        folium.Marker(
            (pos[0], pos[1]),
            icon=folium.Icon(color='gray', icon='flag-checkered', prefix='fa'),
            popup=popup).add_to(self.m)
