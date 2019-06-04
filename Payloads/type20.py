from aisengine import Engine as Template


class Structure(Template):  # Type 20: Data Link Management Message

    def __init__(self):

        super().__init__()

        self.body = {
            'spare': {'type': 'x', 'offset': 38, 'length': 2},
            'offset1': {'type': 'u', 'offset': 40, 'length': 12},
            'number1': {'type': 'u', 'offset': 52, 'length': 4},
            'timeout1': {'type': 'u', 'offset': 56, 'length': 3},
            'increment1': {'type': 'u', 'offset': 59, 'length': 11},
            'offset2': {'type': 'u', 'offset': 70, 'length': 12},
            'number2': {'type': 'u', 'offset': 82, 'length': 4},
            'timeout2': {'type': 'u', 'offset': 86, 'length': 3},
            'increment2': {'type': 'u', 'offset': 89, 'length': 11},
            'offset3': {'type': 'u', 'offset': 100, 'length': 12},
            'number3': {'type': 'u', 'offset': 112, 'length': 4},
            'timeout3': {'type': 'u', 'offset': 116, 'length': 3},
            'increment3': {'type': 'u', 'offset': 119, 'length': 11},
            'offset4': {'type': 'u', 'offset': 130, 'length': 12},
            'number4': {'type': 'u', 'offset': 142, 'length': 4},
            'timeout4': {'type': 'u', 'offset': 146, 'length': 3},
            'increment4': {'type': 'u', 'offset': 149, 'length': 11},
        }

