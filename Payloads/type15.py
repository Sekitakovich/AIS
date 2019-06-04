from aisengine import Engine as Template


class Structure(Template):  # Type 15: Interrogation

    def __init__(self):

        super().__init__()

        self.body = {
            'spare1': {'type': 'x', 'offset': 38, 'length': 2},
            'mmsi1': {'type': 'u', 'offset': 40, 'length': 30},
            'type1_1': {'type': 'u', 'offset': 70, 'length': 6},
            'offset1_1': {'type': 'u', 'offset': 76, 'length': 12},
            'spare2': {'type': 'x', 'offset': 88, 'length': 2},
            'type1_2': {'type': 'u', 'offset': 90, 'length': 6},
            'offset1_2': {'type': 'u', 'offset': 96, 'length': 12},
            'mmsi2': {'type': 'u', 'offset': 110, 'length': 30},
            'type2_1': {'type': 'u', 'offset': 140, 'length': 6},
            'offset2_1': {'type': 'u', 'offset': 146, 'length': 12},
            'spare3': {'type': 'x', 'offset': 158, 'length': 2},
        }

