from contextlib import closing
import socket
from datetime import datetime as dt
import math
import time
from threading import Thread
from flask import Flask
from flask import render_template
from flask import request


class GPRMC(object):

    def __init__(self):

        self.toplat: float = 35.153453  # 浦賀沖
        self.toplng: float = 139.778591

        self.lat: float = 0.0
        self.lng: float = 0.0
        self.sog: float = 0.0
        self.cog: float = 0.0

        self.interval = 1.0
        self.latMeterPerSec = 30.820
        self.lngMeterPerSec = 25.153

        sample = 'GPRMC,085120.307,A,3541.1493,N,13945.3994,E,000.0,240.3,181211,,,A'
        self.rmc = sample.split(',')

        self.group: str = '239.192.0.1'
        self.port: int = 60001

        self.t = Thread(target=self.output, daemon=True)
        self.t.start()

    def GoogleMaptoGPS(self, *, val: float = None) -> float:  # GoogleMaps -> GPGGA

        decimal, integer = math.modf(val)
        value = (integer + ((decimal * 60) / 100)) * 100
        return value

    def checkSum(self, *, body: bytes = b'') -> bytes:

        cs = 0
        for v in body:
            cs ^= v
        return cs

    def update(self, *, sog: float = 0.0, cog: float = 0.0):

        self.sog = sog
        self.cog = cog

    def output(self):

        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

            while True:

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

                nmea = '$%s%s' % (body, cs)
                print(nmea)

                sentence = (nmea + '\r\n').encode()
                try:
                    sock.sendto(sentence, (self.group, self.port))
                except KeyboardInterrupt as e:
                    print(e)
                    break
                else:
                    time.sleep(1)


app = Flask(__name__, static_folder='webcontents', template_folder='webtemplates')
caster = GPRMC()


@app.route('/voyage')
def voyage() -> str:

    sog = int(request.args.get('sog', 0))
    cog = int(request.args.get('cog', 0))
    caster.update(sog=sog, cog=cog)

    return 'OK'


class Main(object):

    def __init__(self):

        app.run(debug=False, host='0.0.0.0', port=8080)


if __name__ == '__main__':

    main = Main()
