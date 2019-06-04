import os
import math
import logging
from datetime import datetime as dt
from datetime import timedelta as td
from threading import Thread
import json
import websocket
import time
from multiprocessing import Queue as MPQueue
from queue import Queue

from dispatcher import Dispatcher
from common import Constants
from archive import Archive


class GPGGA(object):

    def __init__(self, *, quality: int = 0, ss: int = 0):

        self.quality= quality
        self.ss = ss


class Record(object):

    def __init__(self, *, record: dict):

        self.at = dt.utcnow()
        self.record = record


class Session(Thread):

    def __init__(self, *, entrance: Queue):

        super().__init__()
        self.daemon = True

        self.entrance = entrance
        self.counter = 0
        self.deltas = 0
        self.fragment = {}

        while True:
            ws = websocket.create_connection(url='ws://0.0.0.0:%d/' % (Constants.wsport,))
            if ws:
                self.ws = ws
                break
            else:
                time.sleep(1)

        self.dispatcher = Dispatcher()

        self.logger = logging.getLogger('Log')

        self.aq = MPQueue()
        self.archive = Archive(qp=self.aq)
        self.archive.start()

        self.gpgga = GPGGA()
        self.children = [self.dispatcher, self.archive]

    def __del__(self):

        for p in self.children:
            p.join()

    # def _linux_set_time(self, timetuple: tuple):
    #     import ctypes.util
    #     import time
    #
    #     CLOCK_REALTIME = 0
    #
    #     class timespec(ctypes.Structure):
    #         _fields_ = [("tv_sec", ctypes.c_long),
    #                     ("tv_nsec", ctypes.c_long)]
    #
    #     librt = ctypes.CDLL(ctypes.util.find_library("rt"))
    #
    #     ts = timespec()
    #     ts.tv_sec = int(time.mktime(dt(*timetuple[:6]).timetuple()))
    #     ts.tv_nsec = timetuple[6] * 1000000  # Millisecond to nanosecond
    #
    #     librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

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

        # self.logger.debug(msg='Count %06d' % counter)

        try:

            ft = int(nmea[1])  # fragment index
            fn = int(nmea[2])  # fragment total
            ch = nmea[4]  # channel
            payload = nmea[5]
            fillbits = int(nmea[6])

        except (ValueError, IndexError) as e:
            self.logger.debug(msg='%s at %s' % (e, nmea))
            pass
        else:
            doit = False

            if ft > 1:
                id = nmea[3]
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
                result = self.dispatcher.parse(payload=payload, fillbits=fillbits)
                if result.error == result.ErrorCode.noError:

                    thisMMSI = result.member['header']['mmsi']

                    if thisMMSI != 0:

                        info = {
                            'mode': 'AIS',
                            'data': result.member,
                        }
                        news = json.dumps(info)
                        self.broadcast(message=news)

                    else:
                        pass
                        # self.logger.debug(msg='found zero MMSI')
                elif result.error == result.ErrorCode.AIS.type24notCompleted:
                    pass
                elif result.error == result.ErrorCode.AIS.unsupportedType:
                    pass
                else:
                    self.logger.debug('[%s] at %s' % (result.error, nmea))
                    pass

    def atGGA(self, *, nmea: list, counter: int):

        try:
            quality = int(nmea[6])
            ss = int(nmea[7])
        except (IndexError, ValueError) as e:
            self.logger.debug(msg=e)
        else:
            if quality != self.gpgga.quality or ss != self.gpgga.ss:
                self.gpgga.quality = quality
                self.gpgga.ss = ss
                info = {
                    'mode': 'GPGGA',
                    'data': {
                        'quality': quality,
                        'ss': ss,
                    }
                }
                news = json.dumps(info)
                self.broadcast(message=news)

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
            info = {
                'mode': 'GPRMC',
                'data': {
                    'status': status,
                }
            }

            if status == 'A':
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

                    # unix = sysnow + td(microseconds=diff)
                    # print(unix)
                    # if abs(diff) > 60:
                    #     src = (yy, mm, dd, hh, mm, ss, ms)
                    #     self._linux_set_time(timetuple=src)
                    #     self.logger.debug(msg='system date was changed to %s' % str(src))

                    info['data'].update({
                        'lat': float(lat),
                        'lng': float(lng),
                        'ns': str(ns) if ns else '?',
                        'ew': str(ew) if ew else '?',
                        'sog': float(sog) if sog else 0,
                        'cog': float(cog) if cog else 0,
                        'maplat': self.dm2deg(dm=float(lat)),
                        'maplng': self.dm2deg(dm=float(lng)),
                        'ts': rmcnow.timestamp(),
                    })
                except (ValueError,) as e:
                    self.logger.debug(msg=e)
                else:
                    pass
            news = json.dumps(info)
            self.broadcast(message=news)

    def run(self):

        self.logger.debug(msg='process %d' % os.getpid())

        while True:

            sentence = self.entrance.get()

            try:
                nmea = sentence[:-3].split(',')  # cut off checksum
                symbol = nmea[0]
                # prefix = symbol[:-3]
                suffix = symbol[-3:]
            except (ValueError, IndexError) as e:
                self.logger.debug(msg=e)
            else:
                if suffix == 'VDM':
                    self.atVDM(nmea=nmea, counter=self.counter)
                elif suffix == 'RMC':
                    self.atRMC(nmea=nmea, counter=self.counter)
                elif suffix == 'GGA':
                    self.atGGA(nmea=nmea, counter=self.counter)
                else:
                    pass
            finally:

                realtime = dt.utcnow() + td(seconds=self.deltas)
                archive = self.archive.buildUP(at=realtime, nmea=sentence)
                self.aq.put(archive)

                self.counter += 1

