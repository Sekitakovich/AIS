import math
import time
import tkinter as tk
from datetime import datetime as dt
from threading import Thread
import socket
from contextlib import closing


class Bridge(Thread):

    def __init__(self, *, lat: float = 0.0, lng: float = 0.0, ns: str = 'N', ew: str = 'E', interval: float = 1.0,
                 group: str = '0.0.0.0', port: int = 0):
        super().__init__()
        self.daemon = True

        self.latMeterPerSec = 30.820
        self.lngMeterPerSec = 25.153

        self.interval = interval
        self.group = group
        self.port = port

        self.topLat = lat
        self.topLng = lng

        self.lat = lat
        self.lng = lng
        self.ns = ns
        self.ew = ew
        self.sog = 0  # knot
        self.cog = 0  # angle

        sample = 'GPRMC,085120.307,A,3541.1493,N,13945.3994,E,000.0,240.3,181211,,,A'
        self.rmc = sample.split(',')

    def GoogleMaptoGPS(self, *, val: float = None) -> float:  # GoogleMaps -> GPGGA

        decimal, integer = math.modf(val)
        value = (integer + ((decimal * 60) / 100)) * 100
        return value

    def checkSum(self, *, body: bytes = b'') -> bytes:

        cs = 0
        for v in body:
            cs ^= v
        return cs

    def rudder(self, *, starboard: bool = True):

        cog = self.cog
        cog += 1 if starboard else -1
        self.cog = cog % 360

    def throttle(self, *, up: bool = True):

        if up:
            self.sog += 1
        elif self.sog >= 1:
            self.sog -= 1

    def voyage(self) -> str:

        distance = ((self.sog * 1000 * 1.852) / 3600) * self.interval
        theta = math.radians((self.cog * -1) + 90)

        latS = (distance * math.sin(theta)) / self.latMeterPerSec
        self.lat = ((self.lat * 3600) + latS) / 3600

        lngS = (distance * math.cos(theta)) / self.lngMeterPerSec
        self.lng = ((self.lng * 3600) + lngS) / 3600

        now = dt.utcnow()

        self.rmc[1] = now.strftime('%H%M%S.%f')
        self.rmc[3] = '%.4f' % self.GoogleMaptoGPS(val=self.lat)
        self.rmc[5] = '%.4f' % self.GoogleMaptoGPS(val=self.lng)
        self.rmc[7] = '%.1f' % self.sog
        self.rmc[8] = '%.1f' % self.cog
        self.rmc[9] = now.strftime('%y%m%d')

        body = ','.join(self.rmc)
        cs = '*%02X' % self.checkSum(body=body.encode())

        return '$%s%s' % (body, cs)

    def run(self):

        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            while True:
                nmea = self.voyage()
                print(nmea)

                sentence = (nmea + '\r\n').encode()
                try:
                    sock.sendto(sentence, (self.group, self.port))
                except KeyboardInterrupt as e:
                    print(e)
                    break

                time.sleep(self.interval)


class Controller(object):

    def __init__(self, *, bridge: Bridge):

        self.bridge = bridge

        root = tk.Tk()

        frame = tk.Frame(root, width=320, height=100)

        frame.bind('<Any-KeyPress>', self.press)

        frame.focus_set()
        frame.pack()

        root.mainloop()

    def press(self, event):

        keysym = event.keysym

        if keysym == 'Up':
            self.bridge.throttle(up=True)

        elif keysym == 'Down':
            self.bridge.throttle(up=False)

        elif keysym == 'Left':
            self.bridge.rudder(starboard=False)

        elif keysym == 'Right':
            self.bridge.rudder(starboard=True)

        else:
            print('%s' % (keysym,))


if __name__ == '__main__':

    # lat = 34.970497  # 館山付近
    # lng = 139.705098

    # lat = 35.285172  # 三笠
    # lng = 139.674647

    lat = 35.220655  # 久里浜
    lng = 139.714575

    group = '239.192.0.1'
    port = 60001

    cp = Bridge(interval=1.0, lat=lat, lng=lng, group=group, port=port)
    cp.start()

    ooo = Controller(bridge=cp)
