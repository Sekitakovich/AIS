from datetime import datetime as dt

from common import Constants


class AtoN(object):

    def __init__(self):

        self.counter: int = 0
        self.at: dt = dt.utcnow()  # 最終更新日時
        self.status: bool = False

        self.type: int = 0
        self.name: str = ''
        self.lat: float = 0.0
        self.lng: float = 0.0

    def update(self, *, lat: float, lng: float, name: str, type: int):

        self.at = dt.utcnow()
        self.counter += 1

        self.type = type
        self.name = name
        self.lat = lat
        self.lng = lng

        return

    def listup(self):

        return {
            'name': self.name,
            'type': self.type,
            'lat': self.lat,
            'lng': self.lng,
        }


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

        self.expire = Constants.AIS.Expire.static

    def listup(self) -> dict:

        return {
            'name': self.name,
            'imo': self.imo,
            'type': self.type,
            'callsign': self.callsign,
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
        self.flag: str = 'F'

    def listup(self) -> dict:

        return {
            'lat': self.lat,
            'lng': self.lng,
            'sog': self.sog,
            'cog': self.cog,
            'distance': self.distance,
            'angle': self.angle,
            'status': self.status,
            'flag': self.flag,
        }


class Enemy(object):

    def __init__(self):

        self.aisType: Constants.AIS.AIStype = Constants.AIS.AIStype.unknown

        self.static: Statics = Statics()
        self.dynamic: Dynamics = Dynamics()

        return

    def updateStatic(self, *, callsign: str = '', name: str, aistype: Constants.AIS.AIStype, imo: int = 0, version: int = 0, type: int = 0):

        self.static.at = dt.utcnow()  # 最終更新日時

        self.aisType = aistype
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

        self.dynamic.counter += 1
        self.dynamic.status = True

        return
