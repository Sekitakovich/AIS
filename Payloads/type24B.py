from aisengine import Engine as Template


class Structure(Template):  # Type 24: Static Data Report Part B

    def __init__(self):

        super().__init__()

        self.body = {
            'partno': {'type': 'u', 'offset': 38, 'length': 2},
            'shiptype': {'type': 'e', 'offset': 40, 'length': 8},
            'vendorid': {'type': 't', 'offset': 48, 'length': 18},
            'model': {'type': 'u', 'offset': 66, 'length': 4},
            'serial': {'type': 'u', 'offset': 70, 'length': 20},
            'callsign': {'type': 't', 'offset': 90, 'length': 42},
            'to_bow': {'type': 'u', 'offset': 132, 'length': 9},
            'to_stern': {'type': 'u', 'offset': 141, 'length': 9},
            'to_port': {'type': 'u', 'offset': 150, 'length': 6},
            'to_starboard': {'type': 'u', 'offset': 156, 'length': 6},
            'mothership_mmsi': {'type': 'u', 'offset': 132, 'length': 30},
            # 'spare': {'type': 'x', 'offset': 162, 'length': 6},
        }

