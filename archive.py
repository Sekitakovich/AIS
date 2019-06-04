import os
import logging
from datetime import datetime as dt
from multiprocessing import Process
from multiprocessing import Queue as MPQueue

import json
import pathlib
import sqlite3
from queue import Empty


class Archive(Process):

    def __init__(self, *, qp: MPQueue):

        super().__init__()

        self.daemon = True
        self.name = 'Archiver'

        self.qp = qp
        self.counter = 0
        self.current = ''
        self.full = 1000
        self.buffer = []

        self.ymdFormat = '%Y-%m-%d'
        self.hmsFormat = '%H:%M:%S.%f'
        self.tsFormat = '%s %s' % (self.ymdFormat, self.hmsFormat)

        self.folder = 'Archives'
        path = pathlib.Path(self.folder)
        if not path.exists():
            path.mkdir()

        self.logger = logging.getLogger('Log')

    def __del__(self):

        if self.counter > 0:

            self.logger.debug(msg='closing session with commit %d records' % self.counter)
            self.commit()

    def buildUP(self, *, at: dt, nmea: str):
        return json.dumps({
            'ymd': at.strftime(self.ymdFormat),
            'hms': at.strftime(self.hmsFormat),
            'nmea': nmea,
        })

    def commit(self):

        dbname = '%s/%s.db' % (self.folder, self.current)

        # size = len(self.drawer)
        # self.logger.debug(msg='commit %d records' % size)

        db = sqlite3.connect(dbname)
        cursor = db.cursor()

        sql = "CREATE TABLE IF NOT EXISTS 'sentence' ( `id` INTEGER NOT NULL DEFAULT 0 PRIMARY KEY, `hms` text NOT NULL DEFAULT '', `nmea` TEXT NOT NULL DEFAULT '' )"
        cursor.execute(sql)

        sql = 'insert into sentence(hms,nmea) values(?,?)'
        try:
            cursor.executemany(sql, self.buffer)
        except sqlite3.Error as e:
            self.logger.debug(msg=e)
        else:
            pass
        finally:
            self.buffer.clear()

        db.commit()
        db.close()
        self.counter = 0

    def run(self):

        self.logger.debug(msg='process %d' % os.getpid())

        while True:

            try:
                src = json.loads(self.qp.get(block=True, timeout=5))
                pass
            except KeyboardInterrupt as e:
                self.logger.debug(msg=e)
                break
            except json.JSONDecodeError as e:
                self.logger.debug(msg=e)
                pass
            except (Empty,) as e:
                if self.counter > 0:
                    self.commit()
                    self.logger.debug(msg=e)
                pass
            else:
                ymd = src['ymd']
                hms = src['hms']
                nmea = src['nmea']

                if ymd != self.current and self.counter > 0:
                    self.commit()

                self.buffer.append([hms, nmea])
                self.counter += 1

                if self.counter == self.full:
                    self.commit()

                self.current = ymd
