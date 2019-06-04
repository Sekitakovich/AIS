from aisengine import Engine as Template


class Structure(Template):  # Type 12: Addressed Safety-Related Message

    def __init__(self):

        super().__init__()

        self.body = {
            'seqno': {'type': 'x', 'offset': 38, 'length': 2},
            'dest_mmsi': {'type': 'u', 'offset': 40, 'length': 30},
            'retransmit': {'type': 'b', 'offset': 70, 'length': 1},
            'spare': {'type': 'x', 'offset': 71, 'length': 1},
            'text': {'type': 't', 'offset': 72, 'length': 936},
        }

