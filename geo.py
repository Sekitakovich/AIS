from datetime import datetime as dt
from math import sin, cos, tan, atan2, acos, radians, degrees, modf
from threading import Lock


class Target(object):  # notice! lat:lng is GoogleMaps format

    def __init__(self, *, lat: float = 0.0, lng: float = 0.0, sog: float = 0.0, cog: float = 0.0):
        self.lat: float = lat
        self.lng: float = lng
        self.sog: float = sog
        self.cog: float = cog

        return

    def update(self, *, lat: float = 0.0, lng: float = 0.0, sog: float = 0.0, cog: float = 0.0):
        self.lat = lat
        self.lng = lng
        self.sog = sog
        self.cog = cog

        return


class Measurement(object):  # Measurement result

    def __init__(self):
        self.angle: float = 0.0
        self.distance: float = 0.0

        return


class Cockpit(object):  # depend on GPRMC

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
        self.lock = Lock()

        return

    def update(self, *, lat: float = 0.0, lng: float = 0.0, status: bool = False, ns: str = 'N', ew: str = 'E',
               cog: float = 0.0, sog: float = 0.0):

        with self.lock:
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

            self.at = dt.utcnow()

        return

    def dm2deg(self, *, dm: float) -> float:  # GPRMC -> GoogleMaps

        decimal, integer = modf(dm / 100.0)
        value = integer + ((decimal / 60.0) * 100.0)

        return value

    def meter2mile(self, *, meter: float) -> float:
        return meter / 1852

    def mile2meter(self, *, mile: float) -> float:
        return mile * 1852

    def measure(self, *, enemy: Target) -> Measurement:
        x = radians(enemy.lng)
        y = radians(enemy.lat)

        delta = x - self.radLng

        self.relation.angle = degrees(
            atan2(sin(delta), (cos(self.radLat) * tan(y) - sin(self.radLat) * cos(delta))))  # % 360

        self.relation.distance = self.radius * acos(sin(self.radLat) * sin(y) + cos(self.radLat) * cos(y) * cos(delta))

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
        enemy = Target(lat=v['lat'], lng=v['lng'])
        result = cockpit.measure(enemy=enemy)
        mile = cockpit.meter2mile(meter=result.distance)
        print(
            'from [%s] to [%s] : 距離 = %.2f (%.2f) 方位角 = %.2f' % (top['name'], end, result.distance, mile, result.angle))
