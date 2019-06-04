from aisengine import Engine as Template


class Structure(Template):  # Type 17: DGNSS Broadcast Binary Message

    def __init__(self):

        super().__init__()

        self.body = {
            'spare1': {'type': 'x', 'offset': 38, 'length': 2},
            'lon': {'type': 'I4', 'offset': 40, 'length': 18},
            'lat': {'type': 'I4', 'offset': 58, 'length': 17},
            'spare2': {'type': 'x', 'offset': 75, 'length': 5},
            'data': {'type': 'd', 'offset': 80, 'length': 736},
        }

