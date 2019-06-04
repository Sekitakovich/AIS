import os
import logging
from multiprocessing import Process
from multiprocessing import Queue
import serial

from nmea import Inspector


class Receiver(Process):

    def __init__(self, *, port: str, baud: int, mailpost: Queue, name: str):

        super().__init__()

        self.daemon = True
        self.name = name
        self.qp = mailpost
        self.sensor = serial.Serial(port, baudrate=baud)

        self.inspector = Inspector()
        self.logger = logging.getLogger('Log')

    def __del__(self):

        self.logger.debug(msg='Bye Bye!')

    def run(self):

        self.logger.debug(msg='process %d' % os.getpid())

        while True:

            try:
                raw = self.sensor.readline(1024)
            except KeyboardInterrupt as e:
                self.logger.debug(msg=e)
                break
            except serial.SerialException as e:
                self.logger.debug(msg=e)
            else:
                envelope = raw[:-2]  # cut off <CR><LF>
                if self.inspector.checksum(envelope=envelope):
                    self.qp.put(envelope.decode())
                else:
                    self.logger.debug(msg='checksum not match at [%s]' % (envelope,))


if __name__ == '__main__':

    port = '/dev/ttyACM0'
    baud = 9600

    qp = Queue()

    sensor = Receiver(port=port, baud=baud, mailpost=qp)
    sensor.start()

    while True:
        sentence = qp.get()
        print(sentence)
