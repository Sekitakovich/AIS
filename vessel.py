from datetime import datetime as dt
from datetime import timedelta as td

from common import Constants


class Statics(object):

    def __init__(self):

        self.counter = 0

        self.version = 0  # type: int
        self.imo = 0  # type: int
        self.callsign = ''  # type: str
        self.name = ''  # type: str
        self.type = 0  # shiptype


class Dynamics(object):

    def __init__(self):

        self.counter = 0

        self.lat = 0.0  # type: float
        self.lng = 0.0  # type: float
        self.sog = 0.0  # type: float
        self.cog = 0.0  # type: float


class Vessel(object):

    def __init__(self):

        self.at = dt.utcnow()  # 最終更新日時
        self.aisType = Constants.AIStype.unknown

        self.static = Statics()
        self.dynamic = Dynamics()

        self.payloads = {}

    def updateDynamic(self, *, lat: float, lng: float, sog: float, cog: float):

        self.at = dt.utcnow()  # 最終更新日時

        self.dynamic.lat = lat
        self.dynamic.lng = lng
        self.dynamic.sog = sog
        self.dynamic.cog = cog

        self.dynamic.counter += 1

    def updateStatic(self, *, callsign: str = '', name: str, aistype: Constants.AIStype, imo: int = 0, version: int = 0, type: int = 0):

        self.at = dt.utcnow()  # 最終更新日時
        self.aisType = aistype

        self.static.version = version
        self.static.imo = imo
        self.static.callsign = callsign
        self.static.name = name
        self.static.type = type

        self.static.counter += 1
