import logging
import socket
from contextlib import closing
from multiprocessing import Process
from multiprocessing import Queue

from nmea import Inspector


class Receiver(Process):

    def __init__(self, *, mailpost: Queue, name: str = 'fake GPRMC'):
        super().__init__()

        self.daemon = True
        self.name = name
        self.logger = logging.getLogger('Log')
        self.qp = mailpost

        self.thisIPV4 = '0.0.0.0'  # inaddr_any
        self.bufferSize = (1024 * 4)

        self.isMulti = True
        self.thisGroup = '239.192.0.1'
        self.thisPort = 60001

        self.inspector = Inspector()

    def run(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
            if self.isMulti:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                                socket.inet_aton(self.thisGroup) + socket.inet_aton(self.thisIPV4))

            sock.bind(('', self.thisPort))
            sock.settimeout(5)

            while True:
                try:
                    raw, ipv4 = sock.recvfrom(self.bufferSize)  # use blocking
                    pass
                except Exception as e:
                    self.logger.debug(msg=e)
                    # break
                else:
                    envelope = raw[:-2]  # cut off <CR><LF>
                    if self.inspector.checksum(envelope=envelope):
                        self.qp.put(envelope.decode())
                    else:
                        self.logger.debug(msg='checksum not match at [%s]' % (envelope,))


if __name__ == '__main__':

    qp = Queue()
    receiver = Receiver(mailpost=qp)
    receiver.start()

    while True:
        ooo = qp.get()
        print(ooo)
