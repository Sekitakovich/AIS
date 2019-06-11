import logging
from queue import Queue
from multiprocessing import Queue as MPQueue
from typing import Dict, List

from session import Session
# from collector import Collector
from receiver import Receiver
from webserver import Server as WebServer
from wsserver import Server as WSServer
from common import Constants
from gprmc import Receiver as FakeRMC


if __name__ == '__main__':

    logger = logging.getLogger('Log')
    logger.setLevel(logging.DEBUG)
    formatter = '%(asctime)s %(module)s(%(lineno)s):%(funcName)s [%(levelname)s]: %(message)s'
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(logging.Formatter(formatter, datefmt='%H:%M:%S'))
    streamhandler.setLevel(logging.DEBUG)
    logger.addHandler(streamhandler)
    logger.debug('Session start')

    children = []

    mpqueue = MPQueue()
    receiver: Dict[str, dict] = {
        # 'GPS': {
        #     'port': '/dev/ttyACM0',
        #     'baud': 9600,
        # },
        'AIS': {
            'port': '/dev/ttyUSB0',
            'baud': 38400,
        },
    }
    process = {}

    ws = WSServer(port=Constants.wsport)
    ws.start()
    children.append(ws)

    wd = WebServer(name='Flask', osm='webcontents/OSM')
    wd.start()
    children.append(wd)

    for k, v in receiver.items():
        dst = Receiver(port=v['port'], baud=v['baud'], mailpost=mpqueue, name=k)
        dst.start()
        process[k] = dst
        children.append(dst)

    threadqueue = Queue()
    session = Session(entrance=threadqueue)
    session.start()
    children.append(session)

    # collector = Collector(mailpost=mpqueue)
    # collector.start()

    fake = FakeRMC(mailpost=mpqueue)
    fake.start()

    while True:
        try:
            sentence = mpqueue.get()
            threadqueue.put(sentence)
        except KeyboardInterrupt as e:
            logger.debug(msg=e)
            break

    for p in children:
        p.join()

