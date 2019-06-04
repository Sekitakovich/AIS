from aisengine import Engine as Template
from resultbox import ResultBox


class Structure(Template):

    # ClassA 位置通報 1/2/3共通(差異はradioフィールドのみ)

    def __init__(self):

        super().__init__()

        self.body = {
            'status': {'type': 'e', 'offset': 38, 'length': 4},
            'turn': {'type': 'I3', 'offset': 42, 'length': 8},
            'speed': {'type': 'U1', 'offset': 50, 'length': 10},
            'accuracy': {'type': 'b', 'offset': 60, 'length': 1},
            'lon': {'type': 'I4', 'offset': 61, 'length': 28},
            'lat': {'type': 'I4', 'offset': 89, 'length': 27},
            'course': {'type': 'U1', 'offset': 116, 'length': 12},
            'heading': {'type': 'u', 'offset': 128, 'length': 9},
            'second': {'type': 'u', 'offset': 137, 'length': 6},
            'maneuver': {'type': 'e', 'offset': 143, 'length': 2},
            'spare': {'type': 'x', 'offset': 145, 'length': 3},
            'raim': {'type': 'b', 'offset': 146, 'length': 1},
            'radio': {'type': 'u', 'offset': 147, 'length': 19},
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
