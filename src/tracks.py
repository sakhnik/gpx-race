import gpxpy
from itertools import chain, tee


class Tracks:
    def __init__(self, files):
        self.points = [self.get_data(f) for f in files]
        self.center = None
        self.topleft = None
        self.botright = None
        self.calc_extents()

    def get_data(self, file):
        points = []
        gpx = gpxpy.parse(file)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append((point.latitude, point.longitude,
                                   point.speed, point.time))
        return points

    def calc_extents(self):
        t = tee(chain.from_iterable(self.points), 4)
        topleft = (min(p[0] for p in t[0]), min(p[1] for p in t[1]))
        botright = (max(p[0] for p in t[2]), max(p[1] for p in t[3]))
        width = botright[0] - topleft[0]
        height = botright[1] - topleft[1]
        self.center = (topleft[0] + 0.5 * width, topleft[1] + 0.5 * height)
        margin = (width * 0.1, height * 0.1)
        self.topleft = (topleft[0] - margin[0], topleft[1] - margin[1])
        self.botright = (botright[0] + margin[0], botright[1] + margin[1])
