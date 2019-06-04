from aisengine import Engine as Template


class Structure(Template):  # Type 16: Assignment Mode Command

    def __init__(self):

        super().__init__()

        self.body = {
            'spare1': {'type': 'x', 'offset': 38, 'length': 2},
            'mmsi1': {'type': 'u', 'offset': 40, 'length': 30},
            'offset1': {'type': 'u', 'offset': 70, 'length': 12},
            'increment1': {'type': 'u', 'offset': 82, 'length': 10},
            'mmsi2': {'type': 'u', 'offset': 92, 'length': 30},
            'offset2': {'type': 'u', 'offset': 122, 'length': 12},
            'increment2': {'type': 'u', 'offset': 134, 'length': 10},
        }

