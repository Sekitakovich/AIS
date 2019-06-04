from aisengine import Engine as Template


class Structure(Template):  # Type 24: Static Data Report Part A

    def __init__(self):

        super().__init__()

        self.body = {
            'partno': {'type': 'u', 'offset': 38, 'length': 2},
            'shipname': {'type': 't', 'offset': 40, 'length': 120},
            'spare': {'type': 'x', 'offset': 160, 'length': 8},
        }

