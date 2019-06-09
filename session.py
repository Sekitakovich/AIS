import os
import math
import logging
from datetime import datetime as dt
from datetime import timedelta as td
from threading import Thread, Lock
import json
import websocket
import time
from multiprocessing import Queue as MPQueue
from queue import Queue
from typing import List
from typing import Dict

from dispatcher import Dispatcher
from common import Constants
from archive import Archive
from vessel import Vessel


class Cycle(Thread):

    def __init__(self, *, vessel: Dict[int, Vessel], locker: Lock, ws: websocket.create_connection):

        super().__init__()
        self.daemon = True
        self.logger = logging.getLogger('Log')

        self.ws = ws
        self.vessel = vessel
        self.locker = locker

        self.counter = 0
        self.last = dt.utcnow()

    def broadcast(self, *, message: str):
        self.ws.send(message)

    def run(self):

        while True:
            time.sleep(1)
            just = dt.utcnow()
            print('*** Cycle')

            voidlist = []

            with self.locker:
                for mmsi, body in self.vessel.items():
                    dynamic = body.dynamic
                    static = body.static
                    if static.status:
                        if static.at > self.last:
                            # print('static (%d) name = [%s] at %s' % (mmsi, static.name, static.at))
                            info = {
                                'mmsi': mmsi,
                                'type': 'Vs',  # Vessel static
                                'mode': 'i',  # insert
                                'data': static.listup(),
                            }
                            news = json.dumps(info)
                            self.broadcast(message=news)
                        else:
                            ps = (just-static.at).total_seconds()
                            if ps > 60 * 60 * 24:
                                voidlist.append(mmsi)
                            elif ps > 60 * 6:
                                static.status = False

                    if dynamic.status:
                        if dynamic.at > self.last:  # updated
                            # print('dynamic (%d) lat:lng = %f:%f at %s' % (mmsi, dynamic.lat, dynamic.lng, dynamic.at))
                            info = {
                                'mmsi': mmsi,
                                'type': 'Vd',  # Vessel dynamic
                                'mode': '+',
                                'data': dynamic.listup(),
                            }
                            news = json.dumps(info)
                            self.broadcast(message=news)
                        else:
                            ps = (just-dynamic.at).total_seconds()
                            if ps > 60 * 6:
                                dynamic.status = False
                    else:
                        pass

                for mmsi in voidlist:
                    print('void %d' % (mmsi,))
                    del(self.vessel[mmsi])

            self.last = just
            self.counter += 1


class Location(object):

    def __init__(self):

        self.at: dt = dt.utcnow()

        self.status: str = 'N'
        self.lat: float = 0.0
        self.lng: float = 0.0
        self.ns: str = 'N'
        self.ew: str = 'E'
        self.sog: float = 0.0
        self.cog: float = 0.0

    def update(self, *, lat: float, lng: float, ns: str, ew: str, sog: float, cog: float, status: str):

        self.lat = lat
        self.lng = lng
        self.ns = ns
        self.ew = ew
        self.sog = sog
        self.cog = cog
        self.status = status

        self.at = dt.utcnow()

    def listup(self) -> dict:

        return {
            'status': self.status,
            'lat': self.lat,
            'lng': self.lng,
            'ns': self.ns,
            'ew': self.ew,
            'sog': self.sog,
            'cog': self.cog,
        }


class Session(Thread):

    def __init__(self, *, entrance: Queue, name: str = 'Session'):

        super().__init__()
        self.daemon = True
        self.name = name

        self.location = Location()

        self.entrance = entrance
        self.counter: int = 0
        self.deltas: int = 0
        self.fragment: Dict[int, List[str]] = {}

        while True:
            ws = websocket.create_connection(url='ws://0.0.0.0:%d/' % (Constants.wsport,))
            if ws:
                self.ws = ws
                break
            else:
                time.sleep(1)

        self.logger = logging.getLogger('Log')

        self.aq = MPQueue()
        self.archive = Archive(qp=self.aq)
        self.archive.start()

        # self.children = [self.dispatcher, self.archive]
        self.locker = Lock()
        self.dispatcher = Dispatcher()

        self.cycle = Cycle(vessel=self.dispatcher.vessel, locker=self.locker, ws=self.ws)
        self.cycle.start()

    def broadcast(self, *, message: str):
        self.ws.send(message)
        pass

    def dm2deg(self, *, dm: float = None) -> float:  # GPGGA -> GoogleMaps

        decimal, integer = math.modf(dm / 100.0)
        value = integer + ((decimal / 60.0) * 100.0)

        return value

    def deg2dm(self, *, deg: float = None) -> float:  # GoogleMaps -> GPGGA

        decimal, integer = math.modf(deg)
        value = (integer + ((decimal * 60) / 100)) * 100

        return value

    def atVDM(self, *, nmea: list, counter: int):

        try:

            ft: int = int(nmea[1])  # fragment index
            fn: int = int(nmea[2])  # fragment total
            ch: str = nmea[4]  # channel
            payload: str = nmea[5]
            fillbits: int = int(nmea[6])

        except (ValueError, IndexError) as e:
            self.logger.debug(msg='%s at %s' % (e, nmea))
            pass
        else:
            doit = False

            if ft > 1:
                id: int = int(nmea[3])
                if id not in self.fragment:
                    self.fragment[id] = []
                self.fragment[id].append(payload)

                if fn == ft:
                    if len(self.fragment[id]) == ft:
                        payload = ''.join(self.fragment[id])
                        doit = True
                    del(self.fragment[id])
                else:
                    pass
            else:
                doit = True

            if doit:
                with self.locker:
                    result = self.dispatcher.parse(payload=payload, fillbits=fillbits)

                # if result.error == result.ErrorCode.noError:
                #
                #     thisMMSI = result.member['header']['mmsi']
                #
                #     if thisMMSI != 0:
                #         thisType = result.member['header']['type']
                #
                #         info = {
                #             'mode': 'AIS',
                #             'data': result.member,
                #         }
                #         news = json.dumps(info)
                #         self.broadcast(message=news)
                #
                #     else:
                #         pass
                #         # self.logger.debug(msg='found zero MMSI')
                # elif result.error == result.ErrorCode.AIS.type24notCompleted:
                #     pass
                # elif result.error == result.ErrorCode.AIS.unsupportedType:
                #     pass
                # else:
                #     self.logger.debug('[%s] at %s' % (result.error, nmea))
                #     pass

    def atRMC(self, *, nmea: list, counter: int):

        try:

            status = str(nmea[2])

            lat = nmea[3]
            ns = nmea[4]
            lng = nmea[5]
            ew = nmea[6]
            sog = nmea[7]
            cog = nmea[8]

            utc = nmea[1].split('.')

            ymd = nmea[9]

        except (IndexError, ValueError) as e:
            self.logger.debug(msg=e)
        else:
            if status != 'N':
                try:

                    hh = int(utc[0][0:2])
                    mm = int(utc[0][2:4])
                    ss = int(utc[0][4:6])
                    ms = int(utc[1])
                    yy = int(ymd[4:6]) + 2000
                    mm = int(ymd[2:4])
                    dd = int(ymd[0:2])

                    rmcnow = dt(year=yy, month=mm, day=dd, hour=hh, minute=mm, second=ss, microsecond=ms)
                    sysnow = dt.utcnow()
                    self.deltas = (rmcnow - sysnow).total_seconds()

                    self.location.update(
                        # lat=float(lat),
                        # lng=float(lng),
                        ns=str(ns) if ns else '?',
                        ew=str(ew) if ew else '?',
                        sog=float(sog) if sog else 0,
                        cog=float(cog) if cog else 0,
                        lat=self.dm2deg(dm=float(lat)),
                        lng=self.dm2deg(dm=float(lng)),
                        status=status,
                    )

                except (ValueError,) as e:
                    self.logger.debug(msg=e)
                else:
                    pass
            else:
                self.location.status = status  # mmm ...

            info = {
                'mode': 'GPS',
                'data': self.location.listup(),
            }
            news = json.dumps(info)
            self.broadcast(message=news)

    def run(self):

        self.logger.debug(msg='process %d' % os.getpid())

        while True:

            sentence: str = self.entrance.get()

            try:
                nmea: list = sentence[:-3].split(',')  # cut off checksum
                symbol: str = nmea[0]
                # prefix = symbol[:-3]
                suffix: str = symbol[-3:]
            except (ValueError, IndexError) as e:
                self.logger.debug(msg=e)
            else:
                if suffix == 'VDM':
                    self.atVDM(nmea=nmea, counter=self.counter)
                elif suffix == 'RMC':
                    self.atRMC(nmea=nmea, counter=self.counter)
                else:
                    pass
            finally:

                realtime = dt.utcnow() + td(seconds=self.deltas)
                archive = self.archive.buildUP(at=realtime, nmea=sentence)
                self.aq.put(archive)

                self.counter += 1

