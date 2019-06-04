from aisengine import Engine as Template
from resultbox import ResultBox


class Structure(Template):  # Type 6: Binary Addressed Message

    def __init__(self):

        super().__init__()

        self.body = {
            'seqno': {'type': 'u', 'offset': 38, 'length': 2},
            'dest_mmsi': {'type': 'u', 'offset': 40, 'length': 30},
            'retransmit': {'type': 'b', 'offset': 70, 'length': 1},
            'spare': {'type': 'x', 'offset': 71, 'length': 1},
            'dac': {'type': 'u', 'offset': 72, 'length': 10},
            'fid': {'type': 'u', 'offset': 82, 'length': 6},
            # 'data': {'type': 'd', 'offset': 88, 'length': 920},
        }

        self.data = {}

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
