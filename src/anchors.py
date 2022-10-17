import ipyleaflet as ipl
from itertools import chain
import ipywidgets as widgets
import numpy as np
import cv2
import base64


class Anchors:
    def __init__(self, img_map, tracks):
        self.img_map = img_map
        self.image_markers = self.create_markers(tracks,
                                                 self.create_image_icon())
        self.map_markers = self.create_markers(tracks,
                                               self.create_map_icon())

        self.m = ipl.Map(center=tracks.center, zoom=13)
        self.m.add_control(ipl.FullScreenControl())

        layers_control = ipl.LayersControl(position='topright')
        self.m.add_control(layers_control)

        # Aligned image
        aligned_image = ipl.ImageOverlay(
            name='aligned',
            url=self.get_aligned_url(),
            bounds=(tracks.topleft, tracks.botright),
        )
        self.m.add_layer(aligned_image)

        def on_location_changed(event):
            aligned_image.url = self.get_aligned_url()
        for m in chain.from_iterable((self.image_markers, self.map_markers)):
            m.observe(on_location_changed, 'location')

        # Image layer
        lg1 = ipl.LayerGroup(name='Image markers')
        image = ipl.ImageOverlay(
            url=img_map.get_data(),
            bounds=(tracks.topleft, tracks.botright),
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

    def create_image_icon(self):
        return ipl.AwesomeIcon(name='thumbtack', marker_color='red',
                               icon_color='black', spin=False)

    def create_map_icon(self):
        return ipl.AwesomeIcon(name='bullseye', marker_color='blue',
                               icon_color='black', spin=False)

    def create_markers(self, tracks, marker_icon):
        markers = []
        for lat in (tracks.topleft[0], tracks.botright[0]):
            for long in (tracks.topleft[1], tracks.botright[1]):
                mark = ipl.Marker(location=(lat, long), icon=marker_icon)
                markers.append(mark)
        return markers

    def create_opacity_control(self, description, image_widget):
        opacity_slider = widgets.FloatSlider(description=description,
                                             min=0.0, max=1.0, value=1.0)
        widgets.jslink((opacity_slider, 'value'), (image_widget, 'opacity'))
        opacity_control = ipl.WidgetControl(widget=opacity_slider,
                                            position='topright')
        self.m.add_control(opacity_control)

    def _get_aligned_image(self):
        src_points = np.float32([self.img_map.get_xy(*p.location)
                                 for p in self.image_markers])
        dst_points = np.float32([self.img_map.get_xy(*p.location)
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
