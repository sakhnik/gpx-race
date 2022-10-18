import ipywidgets as widgets
from IPython.display import display, FileLink

from finalmap import FinalMap
from tracks import Tracks
from imgmap import ImgMap
from anchors import Anchors


class App:
    def __init__(self):
        self.tracks = None
        self.img_map = None
        self.anchors = None
        self.pictures = []
        self.final_map = None
        self.anchors_out = widgets.Output()
        self.map_out = widgets.Output()

    def get_download_btn(self):
        download_btn = widgets.Button(description="Get the link")
        self.file_link = None

        def on_download_btn_clicked(b):
            if self.file_link:
                return
            self.final_map.m.save('map.html')
            with self.map_out:
                self.file_link = FileLink('map.html')
                display(self.file_link)
        download_btn.on_click(on_download_btn_clicked)
        return download_btn

    def redraw_map_out(self):
        self.map_out.clear_output()
        self.final_map = FinalMap(self.tracks, self.anchors, self.pictures)
        download_btn = self.get_download_btn()
        with self.map_out:
            display(self.final_map.m, download_btn)

    def set_tracks(self, files):
        self.tracks = Tracks(files)
        self.redraw_map_out()

    def set_image(self, img):
        self.img_map = ImgMap(img, self.tracks)
        self.anchors = Anchors(self.img_map, self.tracks)

        plot_btn = widgets.Button(description="Plot the map")
        plot_btn.on_click(lambda b: self.redraw_map_out())

        self.anchors_out.clear_output()
        with self.anchors_out:
            display(self.anchors.m, plot_btn)

    def set_pictures(self, pics):
        self.pictures = pics
        self.redraw_map_out()
