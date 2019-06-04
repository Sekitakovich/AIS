from aisengine import Engine as Template
from resultbox import ResultBox


class Structure(Template):  # Type 8: Binary Broadcast Message

    def __init__(self):

        super().__init__()

        self.body = {
            'spare': {'type': 'x', 'offset': 38, 'length': 2},
            'dac': {'type': 'u', 'offset': 40, 'length': 10},
            'fid': {'type': 'u', 'offset': 50, 'length': 6},
            # 'data': {'type': 'd', 'offset': 56, 'length': 952},
        }

        self.data = {
            1: {
                31: {
                    'lon': {'type': 'I4', 'offset': 56, 'length': 23},
                    'lat': {'type': 'I4', 'offset': 81, 'length': 24},
                    'accuracy': {'type': 'b', 'offset': 103, 'length': 1},
                    'day': {'type': 'u', 'offset': 106, 'length': 5},
                    'hour': {'type': 'u', 'offset': 111, 'length': 5},
                    'minute': {'type': 'u', 'offset': 116, 'length': 6},
                    'wspeed': {'type': 'u', 'offset': 122, 'length': 7},
                    'wgust': {'type': 'u', 'offset': 129, 'length': 7},
                    'wdir': {'type': 'u', 'offset': 136, 'length': 9},
                    'wgustdir': {'type': 'u', 'offset': 145, 'length': 9},
                    'airtemp': {'type': 'I1', 'offset': 154, 'length': 11},
                    'humidity': {'type': 'u', 'offset': 165, 'length': 7},
                    'dewpoint': {'type': 'I1', 'offset': 172, 'length': 10},
                    'pressure': {'type': 'u', 'offset': 182, 'length': 9},
                    'pressuretend': {'type': 'e', 'offset': 191, 'length': 2},
                },
                40: {  # Number of Persons on Board ?
                    'nop': {'type': 'u', 'offset': 56, 'length': 13},
                }
            },
            200: {
                10: {
                    'vin': {'type': 't', 'offset': 56, 'length': 48},
                    'length': {'type': 'u', 'offset': 104, 'length': 13},
                    'beam': {'type': 'u', 'offset': 117, 'length': 10},
                    'shiptype': {'type': 'e', 'offset': 127, 'length': 14},
                    'hazard': {'type': 'e', 'offset': 141, 'length': 3},
                    'draught': {'type': 'u', 'offset': 144, 'length': 11},
                    'loaded': {'type': 'e', 'offset': 155, 'length': 2},
                    'speed_q': {'type': 'b', 'offset': 157, 'length': 1},
                    'course_q': {'type': 'b', 'offset': 158, 'length': 1},
                    'heading_q': {'type': 'b', 'offset': 159, 'length': 1},
                    # 'spare': {'type': 'x', 'offset': 160, 'length': 8},
                },
            }
        }

    def decode(self, *, payload: str) -> ResultBox:

        item = self.parse(payload=payload, table=self.body)

        if item.member['dac'] in self.data:
            dac = self.data[item.member['dac']]
            if item.member['fid'] in dac:
                data = dac[item.member['fid']]
                plus = self.parse(payload=payload, table=data)
                item.member.update(plus.member)
                self.logger.debug(msg=item.member)
            else:
                self.logger.debug('--- not found DAC:FID entry(%d:%d)' % (item.member['dac'], item.member['fid']))
        else:
            self.logger.debug('--- not found DAC:FID entry(%d:%d)' % (item.member['dac'], item.member['fid']))

        return item
