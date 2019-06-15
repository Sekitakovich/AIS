from typing import List
from datetime import datetime as dt
from contextlib import closing
import time
import math
import socket
import logging
from threading import Thread

from common import Constants


class GPRMC(object):

    def __init__(self):

        self.logger = logging.getLogger('Log')

        self.interval: float = 1.0
        self.latMeterPerSec: float = 30.820
        self.lngMeterPerSec: float = 25.153

        self.group: str = Constants.Multicast.group
        self.port: int = Constants.Multicast.port

        # self.toplat: float = 35.153453  # 浦賀沖
        # self.toplng: float = 139.778591

        self.toplat: float = 34.969767  # 浦賀沖
        self.toplng: float = 139.743500

        self.lat: float = self.toplat
        self.lng: float = self.toplng
        self.sog: float = 0.0
        self.cog: float = 0.0

        sample = 'GPRMC,085120.307,A,3541.1493,N,13945.3994,E,000.0,240.3,181211,,,A'
        self.rmc: List[str] = sample.split(',')

        self.running: bool = False
        self.generator: Thread = None

    def GoogleMaptoGPS(self, *, val: float = None) -> float:  # GoogleMaps -> GPGGA

        decimal, integer = math.modf(val)
        value: float = (integer + ((decimal * 60) / 100)) * 100
        return value

    def checkSum(self, *, body: bytes = b'') -> int:

        cs: int = 0
        for v in body:
            cs ^= v
        return cs

    def update(self, *, sog: float = 0.0, cog: float = 0.0, use: bool = False):

        # self.use = use
        self.sog = sog
        self.cog = cog

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

            while self.running:

                distance: float = ((self.sog * 1000 * 1.852) / 3600) * self.interval
                theta: float = math.radians((self.cog * -1) + 90)

                latS: float = (distance * math.sin(theta)) / self.latMeterPerSec
                self.lat = ((self.lat * 3600) + latS) / 3600

                lngS: float = (distance * math.cos(theta)) / self.lngMeterPerSec
                self.lng = ((self.lng * 3600) + lngS) / 3600

                now = dt.utcnow()

                self.rmc[1] = now.strftime('%H%M%S.%f')
                self.rmc[3] = '%.4f' % self.GoogleMaptoGPS(val=self.lat)
                self.rmc[5] = '%.4f' % self.GoogleMaptoGPS(val=self.lng)
                self.rmc[7] = '%.1f' % self.sog
                self.rmc[8] = '%.1f' % self.cog
                self.rmc[9] = now.strftime('%y%m%d')

                body: str = ','.join(self.rmc)
                cs: str = '*%02X' % self.checkSum(body=body.encode())

                nmea: str = '$%s%s' % (body, cs)
                # print(nmea)

                sentence = (nmea + '\r\n').encode()
                try:
                    sock.sendto(sentence, (self.group, self.port))
                except KeyboardInterrupt as e:
                    break
                except socket.error as e:
                    print(e)
                else:
                    pass

                time.sleep(1)
