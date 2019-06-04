from aisengine import Engine as Template
from resultbox import ResultBox


class Structure(Template):  # Type 19: Extended Class B CS Position Report

    def __init__(self):

        super().__init__()

        self.body = {
            'reserved': {'type': 'x', 'offset': 38, 'length': 8},
            'speed': {'type': 'U1', 'offset': 46, 'length': 10},
            'accuracy': {'type': 'b', 'offset': 56, 'length': 1},
            'lon': {'type': 'I4', 'offset': 57, 'length': 28},
            'lat': {'type': 'I4', 'offset': 85, 'length': 27},
            'course': {'type': 'U1', 'offset': 112, 'length': 12},
            'heading': {'type': 'u', 'offset': 124, 'length': 9},
            'second': {'type': 'u', 'offset': 133, 'length': 6},
            'regional': {'type': 'u', 'offset': 139, 'length': 4},
            'shipname': {'type': 't', 'offset': 143, 'length': 120},
            'shiptype': {'type': 'u', 'offset': 263, 'length': 8},
            'to_bow': {'type': 'u', 'offset': 271, 'length': 9},
            'to_stern': {'type': 'u', 'offset': 280, 'length': 9},
            'to_port': {'type': 'u', 'offset': 289, 'length': 6},
            'to_starboard': {'type': 'u', 'offset': 295, 'length': 6},
            'epfd': {'type': 'e', 'offset': 301, 'length': 4},
            'raim': {'type': 'b', 'offset': 305, 'length': 1},
            'assigned': {'type': 'b', 'offset': 307, 'length': 1},
            'spare': {'type': 'x', 'offset': 308, 'length': 4},
        }

    def decode(self, *, payload: str) -> ResultBox:

        item = self.parse(payload=payload, table=self.body)

        item.member['maplat'] = item.member['lat'] / 600000
        item.member['maplng'] = item.member['lon'] / 600000

        return item
