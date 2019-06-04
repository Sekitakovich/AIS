from aisengine import Engine as Template


class Structure(Template):  # Type 14: Safety-Related Broadcast Message

    def __init__(self):

        super().__init__()

        self.body = {
            'seqno': {'type': 'x', 'offset': 38, 'length': 2},
            'text': {'type': 't', 'offset': 40, 'length': 968},
        }

