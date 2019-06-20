import json
import logging
import math
import os
import time
from datetime import datetime as dt
from datetime import timedelta as td
from multiprocessing import Queue as MPQueue
from queue import Queue
from threading import Thread, Lock
from typing import Dict
from typing import List

import websocket

from cockpit import Cockpit
from common import Constants
from dispatcher import Dispatcher
from enemy import Enemy
from enemy import AtoN
from peripheral import MonoLED
from TestAndSamples.buzzer import Buzzer


class Cycle(Thread):

    def __init__(self, *, cockpit: Cockpit, enemy: Dict[int, Enemy], locker: Lock, ws: websocket.create_connection):

        super().__init__()
        self.daemon = True
        self.logger = logging.getLogger('Log')

        self.cockpit = cockpit
        self.ws = ws
        self.enemy = enemy
        self.locker = locker

        self.counter = 0
        self.last = dt.utcnow()

        self.led = MonoLED(bcm=21)
        self.currentMode = self.led.stop
        self.led.set(mode=self.currentMode)

        self.buzzer = Buzzer(bcm=18)
        self.currentJingle = ''

    def alert(self):

        # zone = self.cockpit.zoneMaster[self.cockpit.currentZone]

        nextmode = self.led.stop
        nextJingle: str = ''

        with self.locker:
            for mmsi, body in self.enemy.items():
                dynamic = body.dynamic
                if dynamic.status:
                    if dynamic.flag == 'X':
                        nextmode = self.led.fast
                        nextJingle = 'pupu'
                        break
                    elif dynamic.flag == 'R':
                        nextmode = self.led.slow
                        nextJingle = 'pu'
                        break

        if nextmode != self.currentMode:
            self.logger.debug(msg='mode was changed from %s to %s' % (self.currentMode, nextmode))
            self.led.set(mode=nextmode)
            self.currentMode = nextmode

        # if zone.alert:
        if True:
            if nextJingle != self.currentJingle:
                self.logger.debug(msg='jingle was changed from %s to %s' % (self.currentJingle, nextJingle))
                self.buzzer.push(name=nextJingle)
                self.currentJingle = nextJingle

    def cleanup(self):

        just = dt.utcnow()
        voidlist: List[int] = []

        with self.locker:
            for mmsi, body in self.enemy.items():
                dynamic = body.dynamic
                static = body.static
                if static.status:
                    if static.at > self.last:
                        pass
                    else:
                        ps = (just - static.at).total_seconds()
                        if ps > 60 * 60 * 24:
                            voidlist.append(mmsi)
                        elif ps > 60 * 6:
                            static.status = False

                if dynamic.status:
                    if dynamic.at > self.last:  # updated
                        pass
                    else:
                        ps = (just - dynamic.at).total_seconds()
                        if ps > 60 * 6:
                            dynamic.status = False
                else:
                    pass

        for mmsi in voidlist:
            print('void %d' % (mmsi,))
            del (self.enemy[mmsi])
            pass

    def run(self):

        while True:

            time.sleep(1)
            now = dt.utcnow()

            self.alert()

            if (self.counter % 60) == 0:
                self.cleanup()

            if (now-self.cockpit.at).total_seconds() >= Constants.GPS.timeout:
                info = {
                    'type': 'GPS',
                    'live': False,
                }
                news = json.dumps(info)
                self.ws.send(news)
                pass

            self.counter += 1


class Session(Thread):

    def __init__(self, *, entrance: Queue, name: str = 'Session', aq: MPQueue):

        super().__init__()

        self.daemon = True
        self.name = name

        self.cockpit = Cockpit()
        self.cockpit.update(lat=self.deg2dm(deg=35.297318), lng=self.deg2dm(deg=139.757328), sog=22)
        self.enemy: Dict[int, Enemy] = {}
        self.aton: Dict[int, AtoN] = {}

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

        self.aq = aq

        # self.children = [self.dispatcher, self.archive]
        self.dispatcher = Dispatcher()

        self.locker = Lock()
        self.cycle = Cycle(cockpit=self.cockpit, enemy=self.enemy, locker=self.locker, ws=self.ws)
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

    def typeAtoN(self, *, mmsi: int, name: str, type: int, lat: float, lng: float):

        if mmsi not in self.aton:
            self.aton[mmsi] = AtoN()
        target = self.aton[mmsi]
        target.update(name=name, type=type, lat=lat, lng=lng)

        info = {
            'type': 'AtoN',
            'mmsi': mmsi,
            'data': target.listup(),
        }
        message = json.dumps(info)
        self.broadcast(message=message)

        return

    def profeelEnemy(self, *, mmsi: int, version: int = 0, name: str, imo: int = 0, type: int = 0, callsign: str = '', aistype: Constants.AIS.AIStype = Constants.AIS.AIStype.unknown):

        if mmsi not in self.enemy:
            self.enemy[mmsi] = Enemy()
        target = self.enemy[mmsi]

        target.updateStatic(version=version, name=name, imo=imo, callsign=callsign, aistype=aistype, type=type)

        info = {
            'type': 'AISS',
            'mmsi': mmsi,
            'mode': 'i',  # insert
            'data': target.static.listup(),
        }
        message = json.dumps(info)
        self.broadcast(message=message)

    def actEnemy(self, *, mmsi: int, lat: float, lng: float, sog: float, cog: float):

        if mmsi not in self.enemy:
            self.enemy[mmsi] = Enemy()
        target = self.enemy[mmsi]
        target.updateDynamic(lat=lat, lng=lng, sog=sog, cog=cog)
        measure = self.cockpit.measure(lat=lat, lng=lng)
        flag: str = 'F'  # Far
        zone = self.cockpit.zoneMaster[self.cockpit.currentZone]

        if measure.distance <= zone.red:
            flag = 'X'
            pass
        elif measure.distance <= zone.radius:
            flag = 'R'
            pass
        elif measure.distance <= zone.green:
            flag = 'G'
            pass

        if flag != target.dynamic.flag:
            target.dynamic.flag = flag

        info = {
            'type': 'AISD',
            'mmsi': mmsi,
            'flag': flag,
            'data': target.dynamic.listup(),
        }
        message = json.dumps(info)
        self.broadcast(message=message)

    def patrol(self):

        for mmsi, v in self.enemy.items():
            dynamic = v.dynamic
            self.actEnemy(mmsi=mmsi, lat=dynamic.lat, lng=dynamic.lng, sog=dynamic.sog, cog=dynamic.cog)

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
                    del (self.fragment[id])
                else:
                    pass
            else:
                doit = True

            if doit:
                with self.locker:
                    result = self.dispatcher.parse(payload=payload, fillbits=fillbits)
                    if result.error == result.ErrorCode.noError:
                        header = result.member['header']
                        mmsi = header['mmsi']
                        type = header['type']
                        body = result.member['body']

                        if type in (1, 2, 3, 18, 19):
                            self.actEnemy(mmsi=mmsi, lat=body['maplat'], lng=body['maplng'], sog=body['speed'], cog=body['course'])
                        elif type == 5:
                            self.profeelEnemy(mmsi=mmsi, name=body['shipname'], callsign=body['callsign'], imo=body['imo'], type=body['shiptype'], aistype=Constants.AIS.AIStype.ClassA)
                            pass
                        elif type == 19:
                            self.profeelEnemy(mmsi=mmsi, name=body['shipname'], type=body['shiptype'], aistype=Constants.AIS.AIStype.ClassB_CSTDMA)
                            pass
                        elif type == 24:
                            self.profeelEnemy(mmsi=mmsi, name=body['shipname'], type=body['shiptype'], aistype=Constants.AIS.AIStype.ClassB_SOTDMA)
                            pass
                        elif type == 21:
                            self.typeAtoN(mmsi=mmsi, name=body['name'], type=body['aid_type'], lat=body['maplat'], lng=body['maplng'])
                            pass

    def atRMC(self, *, nmea: list, counter: int):

        try:

            status = str(nmea[2])

            lat = str(nmea[3])
            lng = str(nmea[5])
            ns = str(nmea[4])
            ew = str(nmea[6])
            sog = str(nmea[7])
            cog = str(nmea[8])

            ymd = str(nmea[9])
            utc = str(nmea[1]).split('.')

        except (IndexError, ValueError) as e:
            self.logger.debug(msg=e)
        else:
            if status != 'V':
                try:

                    HH = int(utc[0][0:2])
                    MM = int(utc[0][2:4])
                    SS = int(utc[0][4:6])
                    MS = int(utc[1]) if len(utc) > 1 else 0  # fuck!
                    yy = int(ymd[4:6]) + 2000
                    mm = int(ymd[2:4])
                    dd = int(ymd[0:2])

                except (ValueError,) as e:
                    self.logger.debug(msg=e)
                else:
                    rmcnow = dt(year=yy, month=mm, day=dd, hour=HH, minute=MM, second=SS, microsecond=MS)
                    sysnow = dt.utcnow()
                    self.deltas = (rmcnow - sysnow).total_seconds()

                    self.cockpit.update(
                        lat=float(lat),
                        lng=float(lng),
                        ns=str(ns) if ns else '?',
                        ew=str(ew) if ew else '?',
                        sog=float(sog) if sog else 0,
                        cog=float(cog) if cog else 0,
                        status=status == 'A',
                    )
                    pass

                    # --------------------------------------------------------------------------------
                    self.patrol()
                    # --------------------------------------------------------------------------------

            else:
                pass

            info = {
                'type': 'GPS',
                'live': True,
                'data': self.cockpit.listup(),
            }
            news = json.dumps(info)
            self.broadcast(message=news)

    def buildUP(self, *, at: dt, nmea: str):
        return json.dumps({
            'ymd': at.strftime(Constants.SQLite.ymdFormat),
            'hms': at.strftime(Constants.SQLite.hmsFormat),
            'nmea': nmea,
        })

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
                    pass
                elif suffix == 'RMC':
                    self.atRMC(nmea=nmea, counter=self.counter)
                    pass
                else:
                    pass
            finally:

                realtime = dt.utcnow() + td(seconds=self.deltas)
                archive = self.buildUP(at=realtime, nmea=sentence)
                self.aq.put(archive)

                self.counter += 1
