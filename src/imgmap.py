from PIL import Image
import io
import base64
import cv2
import numpy as np


class ImgMap:
    def __init__(self, img, tracks):
        self.img = img
        self.tracks = tracks
        self.image_file = Image.open(io.BytesIO(self.img))

    def get_data(self):
        data = 'data:image/png;base64,'
        data += base64.b64encode(self.img).decode('utf-8')
        return data

    def get_size(self):
        return self.image_file.size

    def get_xy(self, lat, lon):
        w, h = self.get_size()
        tracks = self.tracks
        x = w * (lon - tracks.topleft[1]) \
            / (tracks.botright[1] - tracks.topleft[1])
        y = h * (tracks.botright[0] - lat) \
            / (tracks.botright[0] - tracks.topleft[0])
        return x, y

    def get_for_cv(self):
        return cv2.cvtColor(np.array(self.image_file), cv2.COLOR_RGB2BGR)
