from aisengine import Engine as Template
from resultbox import ResultBox


class Structure(Template):

    '''
    ClassB 標準位置通報(SO/CS共通: 差異はradioフィールドのみ)
    '''

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
            'regional': {'type': 'u', 'offset': 139, 'length': 2},
            'cs': {'type': 'b', 'offset': 141, 'length': 1},
            'display': {'type': 'b', 'offset': 142, 'length': 1},
            'dsc': {'type': 'b', 'offset': 143, 'length': 1},
            'band': {'type': 'b', 'offset': 144, 'length': 1},
            'msg22': {'type': 'b', 'offset': 145, 'length': 1},
            'assigned': {'type': 'b', 'offset': 146, 'length': 1},
            'raim': {'type': 'b', 'offset': 147, 'length': 1},
            'radio': {'type': 'u', 'offset': 148, 'length': 20},
        }

    def decode(self, *, payload: str) -> ResultBox:

        item = self.parse(payload=payload, table=self.body)

        item.member['maplat'] = item.member['lat'] / 600000
        item.member['maplng'] = item.member['lon'] / 600000

        return item
