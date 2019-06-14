from threading import Thread
import time
import sqlite3
from contextlib import closing
import socket
import logging

from common import Constants


class Emulator(object):

    def __init__(self):

        self.logger = logging.getLogger('Log')

        self.file = Constants.Emulator.aislog
        self.port = Constants.Multicast.port
        self.group = Constants.Multicast.group

        self.running: bool = False
        self.generator: Thread = None

    def update(self, *, use: bool = False):

        if self.running and (use is False):
            self.running = False
            self.generator.join()
            self.logger.debug(msg='switch OFF')
            pass
        elif (self.running is False) and use:
            self.running = True
            self.generator = Thread(target=self.output, daemon=True)
            self.generator.start()
            self.logger.debug(msg='switch ON')
            pass

    def output(self):

        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            with closing(sqlite3.connect(self.file)) as db:

                db.row_factory = sqlite3.Row
                cursor = db.cursor()
                query = 'select * from sentence order by id asc'
                cursor.execute(query)

                for index, row in enumerate(cursor, 1):

                    if self.running is False:
                        break
                    else:
                        nmea = row['nmea']
                        if nmea[3:6] == 'VDM':
                            delta = row['delta']
                            if delta:
                                time.sleep(delta)
                            sentence = (nmea + '\r\n').encode()
                            # print('%08d (%.3f) %s: %s' % (index, delta, row['hms'], row['nmea']))
                            try:
                                sock.sendto(sentence, (self.group, self.port))
                            except KeyboardInterrupt as e:
                                print(e)
                                break


if __name__ == '__main__':

    emulator = Emulator()



