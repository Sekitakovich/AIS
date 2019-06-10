from datetime import datetime as dt
from math import sin, cos, tan, atan2, acos, radians, degrees, modf
from typing import List

from routine import Measurement


class Zone(object):

    def __init__(self, *, radius: float, sog: int, zoom: int):
        self.radius: float = radius  # radius of guard zone meter
        self.sog: int = sog  # notice! knot
        self.zoom: int = zoom  # OSM zoomlevel

        self.red = radius / 2
        self.green = radius * 2


class Cockpit(object):  # this vessel's cockpit depend on GPRMC

    def __init__(self):
        self.utc: dt = dt.utcnow()
        self.status: bool = False
        self.lat: float = 0.0
        self.ns: str = 'N'
        self.lng: float = 0.0
        self.ew: str = 'E'
        self.sog: float = 0.0  # knot
        self.cog: float = 0.0  # 0 - 359.9
        self.mode: str = 'N'  # N:A:D:E

        self.mapLat = 0.0
        self.mapLng = 0.0
        self.radLat: float = 0.0  # radian
        self.radLng: float = 0.0  # radian

        self.at: dt = dt.utcnow()
        self.relation = Measurement()

        self.radius: float = 6378.137 * 1000  # 地球の半径(m)

        self.zoneMaster: List[Zone] = [
            Zone(radius=0.125, zoom=16, sog=5),
            Zone(radius=0.250, zoom=15, sog=10),
            Zone(radius=0.5, zoom=14, sog=15),
            Zone(radius=1, zoom=13, sog=20),
            Zone(radius=2, zoom=12, sog=25),
            Zone(radius=4, zoom=11, sog=40),
            # Zone(radius=8, zoom=10, sog=10000),
        ]
        self.currentZone: int = 0

        return

    def update(self, *, lat: float = 0.0, lng: float = 0.0, status: bool = False, ns: str = 'N', ew: str = 'E',
               cog: float = 0.0, sog: float = 0.0):

        self.status = status
        self.lat = lat
        self.lng = lng
        self.ns = ns
        self.ew = ew
        self.cog = cog
        self.sog = sog

        self.mapLat = self.dm2deg(dm=lat)
        self.mapLng = self.dm2deg(dm=lng)
        self.radLat = radians(self.mapLat)
        self.radLng = radians(self.mapLng)

        for index, z in enumerate(self.zoneMaster):
            if sog <= z.sog:
                self.currentZone = index
                break

        self.at = dt.utcnow()

        return

    def listup(self) -> dict:

        return {
            'status': self.status,
            'lat': self.mapLat,
            'lng': self.mapLng,
            'ns': self.ns,
            'ew': self.ew,
            'sog': self.sog,
            'cog': self.cog,
        }

    def dm2deg(self, *, dm: float) -> float:  # GPRMC -> GoogleMaps

        decimal, integer = modf(dm / 100.0)
        value = integer + ((decimal / 60.0) * 100.0)

        return value

    def meter2mile(self, *, meter: float) -> float:
        return meter / 1852

    def mile2meter(self, *, mile: float) -> float:
        return mile * 1852

    def measure(self, *, lat: float, lng: float) -> Measurement:  # format is GoogleMaps
        x = radians(lng)
        y = radians(lat)

        delta = x - self.radLng

        self.relation.angle = degrees(
            atan2(sin(delta), (cos(self.radLat) * tan(y) - sin(self.radLat) * cos(delta))))  # % 360

        distance = self.radius * acos(sin(self.radLat) * sin(y) + cos(self.radLat) * cos(y) * cos(delta))
        self.relation.distance = self.meter2mile(meter=distance)

        return self.relation


if __name__ == '__main__':

    def deg2dm(deg: float) -> float:  # GoogleMaps -> GPRMC

        decimal, integer = modf(deg)
        value = (integer + ((decimal * 60) / 100)) * 100

        return value


    top = {
        'lat': 35.602192,
        'lng': 139.367282,
        'name': '京王多摩境駅',
    }

    cockpit = Cockpit()
    cockpit.update(lat=deg2dm(deg=top['lat']), lng=deg2dm(deg=top['lng']))

    e = {
        '京王多摩センター駅': {'lat': 35.625496, 'lng': 139.424912},
        '京王橋本駅': {'lat': 35.595134, 'lng': 139.344944},
        'JR八王子駅': {'lat': 35.656592, 'lng': 139.338960},
        '小田急町田駅': {'lat': 35.545263, 'lng': 139.445027},
    }

    for end, v in e.items():
        result = cockpit.measure(lat=v['lat'], lng=v['lng'])
        mile = cockpit.meter2mile(meter=result.distance)
        print(
            'from [%s] to [%s] : 距離 = %.2f (%.2f) 方位角 = %.2f' % (top['name'], end, result.distance, mile, result.angle))
