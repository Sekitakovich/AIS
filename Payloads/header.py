from aisengine import Engine as Template


class Structure(Template):  # Common header

    def __init__(self):

        super().__init__()

        self.body = {
            'type': {'type': 'u', 'offset': 0, 'length': 6},
            'repeat': {'type': 'u', 'offset': 6, 'length': 2},
            'mmsi': {'type': 'u', 'offset': 8, 'length': 30},
        }

