from aisengine import Engine as Template


class Structure(Template):

    '''
    ClassA 静的データ
    '''

    def __init__(self):

        super().__init__()

        self.body = {
            'ais_version': {'type': 'u', 'offset': 38, 'length': 2},
            'imo': {'type': 'u', 'offset': 40, 'length': 30},
            'callsign': {'type': 't', 'offset': 70, 'length': 42},
            'shipname': {'type': 't', 'offset': 112, 'length': 120},
            'shiptype': {'type': 'u', 'offset': 232, 'length': 8},
            'to_bow': {'type': 'u', 'offset': 240, 'length': 9},
            'to_stern': {'type': 'u', 'offset': 249, 'length': 9},
            'to_port': {'type': 'u', 'offset': 258, 'length': 6},
            'to_starboard': {'type': 'u', 'offset': 264, 'length': 6},
            'epfd': {'type': 'u', 'offset': 270, 'length': 4},
            'month': {'type': 'u', 'offset': 274, 'length': 4},
            'day': {'type': 'u', 'offset': 278, 'length': 5},
            'hour': {'type': 'u', 'offset': 283, 'length': 5},
            'minute': {'type': 'u', 'offset': 288, 'length': 6},
            'draught': {'type': 'U1', 'offset': 294, 'length': 8},
            'destination': {'type': 't', 'offset': 302, 'length': 120},
            'dte': {'type': 'u', 'offset': 422, 'length': 1},
        }


if __name__ == '__main__':

    s = '55?MbV02;H;s<HtKR20EHE:0@T4@Dn2222222216L961O5Gf0NSQEp6ClRp888888888880'

    ooo = Structure()
    item = ooo.decode(payload=s)
    print(item)
