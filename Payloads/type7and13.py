from aisengine import Engine as Template


class Structure(Template):  # Type 7: Binary Acknowledge

    def __init__(self):

        super().__init__()

        self.body = {
            'spare': {'type': 'x', 'offset': 38, 'length': 2},
            'mmsi1': {'type': 'u', 'offset': 40, 'length': 30},
            'mmsiseq1': {'type': 'u', 'offset': 70, 'length': 2},
            'mmsi2': {'type': 'u', 'offset': 72, 'length': 30},
            'mmsiseq2': {'type': 'u', 'offset': 102, 'length': 2},
            'mmsi3': {'type': 'u', 'offset': 104, 'length': 30},
            'mmsiseq3': {'type': 'u', 'offset': 134, 'length': 2},
            'mmsi4': {'type': 'u', 'offset': 136, 'length': 30},
            'mmsiseq4': {'type': 'u', 'offset': 166, 'length': 2},
        }

