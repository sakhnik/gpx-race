from PIL import Image
import io
import base64
import cv2
import numpy as np


class ImgMap:
    def __init__(self, img):
        self.img = img
        self.image_file = Image.open(io.BytesIO(self.img))

    def get_data(self):
        data = 'data:image/png;base64,'
        data += base64.b64encode(self.img).decode('utf-8')
        return data

    def get_size(self):
        return self.image_file.size

    def get_width_height(self):
        return self.get_size()

    def get_for_cv(self):
        return cv2.cvtColor(np.array(self.image_file), cv2.COLOR_RGB2BGR)
