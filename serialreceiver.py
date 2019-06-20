import os
import logging
from multiprocessing import Process
from multiprocessing import Queue
import serial
import setproctitle

from nmea import Inspector


class Receiver(Process):

    def __init__(self, *, port: str, baud: int, mailpost: Queue, name: str):

        super().__init__()

        self.daemon = True
        self.name = name

        setproctitle.setproctitle('EE'+name)

        self.ready = True

        self.qp = mailpost
        self.port = port

        self.inspector = Inspector()
        self.logger = logging.getLogger('Log')

        try:
            self.sensor = serial.Serial(port, baudrate=baud)
        except (serial.SerialException, ) as e:
            self.ready = False
            self.logger.debug(msg=e)
        else:
            pass

    # def __del__(self):
    #
    #     self.logger.debug(msg='Bye Bye!')

    def run(self):

        if self.ready:
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
        else:
            self.logger.debug(msg='%s(%s) not ready' % (self.name, self.port))


if __name__ == '__main__':

    logger = logging.getLogger('Log')
    logger.setLevel(logging.DEBUG)
    formatter = '%(asctime)s %(module)s(%(lineno)s):%(funcName)s [%(levelname)s]: %(message)s'
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(logging.Formatter(formatter, datefmt='%H:%M:%S'))
    streamhandler.setLevel(logging.DEBUG)
    logger.addHandler(streamhandler)
    logger.debug('Session start')

    port = '/dev/ttyUSB0'
    baud = 9600

    qp = Queue()

    sensor = Receiver(port=port, baud=baud, mailpost=qp, name='SerialListner')
    sensor.start()

    while True:
        sentence = qp.get()
        print(sentence)
