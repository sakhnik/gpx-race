import ipyleaflet as ipl
from itertools import chain
import ipywidgets as widgets
import numpy as np
import cv2
import base64


class Anchors:
    def __init__(self, img_map, tracks, storage):
        self.img_map = img_map
        self.storage = storage

        self.image_data = img_map.get_data()
        # Load the previous anchor points if possible, or calculate from tracks
        anchors = storage.load_anchors(self.image_data)
        if not anchors:
            anchors = self._get_default_anchors(tracks)
            storage.save_anchors(self.image_data, anchors)
        self.corners = anchors["corners"]

        self.image_markers = self.create_markers(anchors["image"],
                                                 self.create_image_icon())
        self.map_markers = self.create_markers(anchors["map"],
                                               self.create_map_icon())

        self.m = ipl.Map(center=tracks.center, zoom=13)
        self.m.add_control(ipl.FullScreenControl())

        layers_control = ipl.LayersControl(position='topright')
        self.m.add_control(layers_control)

        # Aligned image
        aligned_image = ipl.ImageOverlay(
            name='aligned',
            url=self.get_aligned_url(),
            bounds=self.get_bounds(),
        )
        self.m.add_layer(aligned_image)

        def on_location_changed(event):
            aligned_image.url = self.get_aligned_url()
        for m in chain.from_iterable((self.image_markers, self.map_markers)):
            m.observe(on_location_changed, 'location')

        # Image layer
        lg1 = ipl.LayerGroup(name='Image markers')
        image = ipl.ImageOverlay(
            url=self.image_data,
            bounds=self.get_bounds(),
        )
        lg1.add_layer(image)

        for m in self.image_markers:
            lg1.add_layer(m)
        self.m.add_layer(lg1)

        self.create_opacity_control('Original:', image)
        self.create_opacity_control('Aligned:', aligned_image)

        # Track layer
        lg2 = ipl.LayerGroup(name='Map markers')
        track = ipl.Polyline(
            locations=[[p[0], p[1]] for p in tracks.points[0]],
            color='red',
            weight=2,
            fill=False,
            opacity=0.6
        )
        lg2.add_layer(track)

        for m in self.map_markers:
            lg2.add_layer(m)
        self.m.add_layer(lg2)

    def _get_default_anchors(self, tracks):
        locations = []
        for lat in (tracks.topleft[0], tracks.botright[0]):
            for long in (tracks.topleft[1], tracks.botright[1]):
                locations.append([lat, long])
        anchors = {
            "image": locations,
            "map": locations,
            "corners": {"topleft": tracks.topleft,
                        "botright": tracks.botright}
        }
        return anchors

    def get_bounds(self):
        tl = self.corners["topleft"]
        br = self.corners["botright"]
        return tl, br

    def create_image_icon(self):
        return ipl.AwesomeIcon(name='thumbtack', marker_color='red',
                               icon_color='black', spin=False)

    def create_map_icon(self):
        return ipl.AwesomeIcon(name='bullseye', marker_color='blue',
                               icon_color='black', spin=False)

    def create_markers(self, locations, marker_icon):
        markers = []
        for loc in locations:
            mark = ipl.Marker(location=(loc[0], loc[1]), icon=marker_icon)
            markers.append(mark)
        return markers

    def create_opacity_control(self, description, image_widget):
        opacity_slider = widgets.FloatSlider(description=description,
                                             min=0.0, max=1.0, value=1.0)
        widgets.jslink((opacity_slider, 'value'), (image_widget, 'opacity'))
        opacity_control = ipl.WidgetControl(widget=opacity_slider,
                                            position='topright')
        self.m.add_control(opacity_control)

    def get_xy(self, lat, lon):
        w, h = self.img_map.get_width_height()
        tl, br = self.get_bounds()
        x = w * (lon - tl[1]) / (br[1] - tl[1])
        y = h * (br[0] - lat) / (br[0] - tl[0])
        return x, y

    def _get_aligned_image(self):
        # Store the current anchors positions to the DB
        anchors = {
            "image": [p.location for p in self.image_markers],
            "map": [p.location for p in self.map_markers],
            "corners": self.corners
        }
        self.storage.save_anchors(self.image_data, anchors)

        # Apply the transformation
        src_points = np.float32([self.get_xy(*p.location)
                                 for p in self.image_markers])
        dst_points = np.float32([self.get_xy(*p.location)
                                 for p in self.map_markers])
        mat = cv2.getPerspectiveTransform(src_points, dst_points)
        img = self.img_map.get_for_cv()
        img = cv2.warpPerspective(img, mat, self.img_map.get_size())
        is_ok, aligned_map = cv2.imencode('.jpg', img)
        if not is_ok:
            raise "Failed to align the image"
        return aligned_map

    def get_aligned_url(self):
        aligned_url = 'data:image/jpeg;base64,'
        aligned_url += base64.b64encode(self._get_aligned_image()) \
            .decode('utf-8')
        return aligned_url
