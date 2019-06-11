from datetime import datetime as dt
from datetime import timedelta as td

from common import Constants
from cockpit import Cockpit


class Statics(object):

    def __init__(self):

        self.counter: int = 0
        self.at: dt = dt.utcnow()  # 最終更新日時
        self.status: bool = False

        self.version: int = 0
        self.imo: int = 0
        self.callsign: str = ''
        self.name: str = ''
        self.type: int = 0

    def listup(self) -> dict:

        return {
            'name': self.name,
            'type': self.type,
        }


class Dynamics(object):

    def __init__(self):

        self.counter: int = 0
        self.at: dt = dt.utcnow()  # 最終更新日時
        self.status: bool = False

        self.lat: float = 0.0
        self.lng: float = 0.0
        self.sog: float = 0.0
        self.cog: float = 0.0

        self.distance: float = 0.0
        self.angle: float = 0.0
        # self.flag: str = '?'

    def listup(self) -> dict:

        return {
            'lat': self.lat,
            'lng': self.lng,
            'sog': self.sog,
            'cog': self.cog,
            'distance': self.distance,
            'angle': self.angle,
            'status': self.status,
            # 'signal': self.flag,
        }


class Enemy(object):

    def __init__(self, *, cockpit: Cockpit):

        self.aisType: Constants.AIStype = Constants.AIStype.unknown

        self.cockpit = cockpit

        self.static: Statics = Statics()
        self.dynamic: Dynamics = Dynamics()

        return

    def updateStatic(self, *, callsign: str = '', name: str, aistype: Constants.AIStype, imo: int = 0, version: int = 0, type: int = 0):

        self.aisType = aistype
        self.static.at = dt.utcnow()  # 最終更新日時

        self.static.version = version
        self.static.imo = imo
        self.static.callsign = callsign
        self.static.name = name
        self.static.type = type

        self.static.counter += 1
        self.static.status = True

        return

    def updateDynamic(self, *, lat: float, lng: float, sog: float, cog: float):

        self.dynamic.at = dt.utcnow()  # 最終更新日時

        self.dynamic.lat = lat
        self.dynamic.lng = lng
        self.dynamic.sog = sog
        self.dynamic.cog = cog

        measure = self.cockpit.measure(lat=lat, lng=lng)
        self.dynamic.distance = measure.distance
        self.dynamic.angle = measure.angle

        # zone = self.cockpit.zoneMaster[self.cockpit.currentZone]
        # color: str = 'F'  # Far
        # if self.dynamic.distance <= zone.red:
        #     color = 'R'
        #     pass
        # elif self.dynamic.distance <= zone.radius:
        #     color = 'Y'
        #     pass
        # elif self.dynamic.distance <= zone.green:
        #     color = 'G'
        #     pass
        #
        # self.dynamic.flag = color

        self.dynamic.counter += 1
        self.dynamic.status = True

        return

