import gpxpy
from itertools import chain, tee
import re


class Tracks:
    def __init__(self, files):
        def drop_ext(fname):
            return re.sub(r"\.gpx$", "", fname, re.IGNORECASE)
        self.names = [drop_ext(f['metadata']['name']) for f in files]
        self.points = [self.get_data(f['content']) for f in files]
        self.center = None
        self.topleft, self.botright = self.calc_extents()
        self.results = self.calc_results()

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
        topleft = (topleft[0] - margin[0], topleft[1] - margin[1])
        botright = (botright[0] + margin[0], botright[1] + margin[1])
        return topleft, botright

    def calc_results(self):
        results = [(i, (p[-1][3] - p[0][3]))
                   for i, p in enumerate(self.points)]
        results.sort(key=lambda x: x[1])
        return results
