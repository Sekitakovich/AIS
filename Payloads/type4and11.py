from aisengine import Engine as Template
from resultbox import ResultBox


class Structure(Template):

    def __init__(self):

        super().__init__()

        self.body = {
            'year': {'type': 'u', 'offset': 38, 'length': 14},
            'month': {'type': 'u', 'offset': 52, 'length': 4},
            'day': {'type': 'u', 'offset': 56, 'length': 5},
            'hour': {'type': 'u', 'offset': 61, 'length': 5},
            'minute': {'type': 'u', 'offset': 66, 'length': 6},
            'second': {'type': 'u', 'offset': 72, 'length': 6},
            'accuracy': {'type': 'b', 'offset': 78, 'length': 1},
            'lon': {'type': 'I4', 'offset': 79, 'length': 28},
            'lat': {'type': 'I4', 'offset': 107, 'length': 27},
            'epfd': {'type': 'e', 'offset': 134, 'length': 4},
            'spare': {'type': 'x', 'offset': 138, 'length': 10},
            'raim': {'type': 'b', 'offset': 148, 'length': 1},
            'radio': {'type': 'u', 'offset': 149, 'length': 19},
        }

    def decode(self, *, payload: str) -> ResultBox:

        item = self.parse(payload=payload, table=self.body)

        item.member['maplat'] = item.member['lat'] / 600000
        item.member['maplng'] = item.member['lon'] / 600000

        return item
