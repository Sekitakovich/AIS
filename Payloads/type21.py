from aisengine import Engine as Template
from resultbox import ResultBox


class Structure(Template):  # Type 21: Aid-to-Navigation Report

    def __init__(self):

        super().__init__()

        self.body = {
            'aid_type': {'type': 'e', 'offset': 38, 'length': 5},
            'name': {'type': 't', 'offset': 43, 'length': 120},
            'accuracy': {'type': 'b', 'offset': 163, 'length': 1},
            'lon': {'type': 'I4', 'offset': 164, 'length': 28},
            'lat': {'type': 'I4', 'offset': 192, 'length': 27},
            'to_bow': {'type': 'u', 'offset': 219, 'length': 9},
            'to_stern': {'type': 'u', 'offset': 228, 'length': 9},
            'to_port': {'type': 'u', 'offset': 237, 'length': 6},
            'to_starboard': {'type': 'u', 'offset': 243, 'length': 6},
            'epfd': {'type': 'e', 'offset': 249, 'length': 4},
            'second': {'type': 'x', 'offset': 253, 'length': 6},
            'off_position': {'type': 'b', 'offset': 259, 'length': 1},
            'regional': {'type': 'u', 'offset': 260, 'length': 8},
            'raim': {'type': 'b', 'offset': 268, 'length': 1},
            'virtual_aid': {'type': 'b', 'offset': 269, 'length': 1},
            'assigned': {'type': 'b', 'offset': 270, 'length': 1},
            'spare': {'type': 'x', 'offset': 271, 'length': 1},
            'extension': {'type': 't', 'offset': 272, 'length': 88},
        }

    def decode(self, *, payload: str) -> ResultBox:

        item = self.parse(payload=payload, table=self.body)

        item.member['maplat'] = item.member['lat'] / 600000
        item.member['maplng'] = item.member['lon'] / 600000

        return item
