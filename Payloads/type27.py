from aisengine import Engine as Template
from resultbox import ResultBox


class Structure(Template):  # Type 27: Long Range AIS Broadcast message

    def __init__(self):

        super().__init__()

        self.body = {
            'accuracy': {'type': 'b', 'offset': 38, 'length': 1},
            'raim': {'type': 'b', 'offset': 39, 'length': 1},
            'status': {'type': 'e', 'offset': 40, 'length': 4},
            'lon': {'type': 'I4', 'offset': 44, 'length': 28},
            'lat': {'type': 'I4', 'offset': 62, 'length': 27},
            'speed': {'type': 'U1', 'offset': 79, 'length': 6},  # 0-62(kn) 63 == invalid
            'course': {'type': 'U1', 'offset': 85, 'length': 9},  # 0-359 511 == invalid
            'gnss': {'type': 'b', 'offset': 94, 'length': 1},
            'spare': {'type': 'x', 'offset': 95, 'length': 1},
        }

    def decode(self, *, payload: str) -> ResultBox:

        item = self.parse(payload=payload, table=self.body)

        item.member['maplat'] = item.member['lat'] / 600000
        item.member['maplng'] = item.member['lon'] / 600000

        return item


if __name__ == '__main__':

    type1 = '15RTgt0PAso;90TKcjM8h6g208CQ'

    ooo = Structure()
    item = ooo.decode(payload=type1)
    print(item)
