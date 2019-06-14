import ctypes
import logging


class Inspector(object):

    def __init__(self):

        self.logger = logging.getLogger('Log')

        so = 'clib/libCheckSum.so'
        self.libcsum = ctypes.CDLL(so)

    def checksum(self, *, envelope: bytes) -> bool:

        try:
            body = envelope[1:-3]
            your = int(envelope[-2:], 16)
        except (IndexError, ValueError) as e:
            # self.logger.debug(msg='%s at [%s]' % (e, envelope))
            return False
        else:
            mine = self.libcsum.checksum(body, len(body))
            return your == mine


if __name__ == '__main__':

    ooo = Inspector()

    src = b'!AIVDM,1,1,,B,177KQJ5000G?tO`K>RA1wUbN0TKH,0*5C'

    ok = ooo.checksum(envelope=src)
    print(ok)