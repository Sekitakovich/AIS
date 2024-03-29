import logging
from queue import Queue as ThreadQueue
from multiprocessing import Queue as MPQueue, current_process
from typing import Dict, List
import setproctitle

from session import Session
from serialreceiver import Receiver
from webserver import Server as WebServer
from wsserver import Server as WSServer
from common import Constants
from udplistner import Receiver as UDPListner
from archive import Archive


if __name__ == '__main__':

    logger = logging.getLogger('Log')
    logger.setLevel(logging.DEBUG)
    formatter = '%(asctime)s %(module)s(%(lineno)s):%(funcName)s [%(levelname)s]: %(message)s'
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(logging.Formatter(formatter, datefmt='%H:%M:%S'))
    streamhandler.setLevel(logging.DEBUG)
    logger.addHandler(streamhandler)
    logger.debug('Session start')

    mpqueue = MPQueue()  # queue for multiprocessing
    threadqueue = ThreadQueue()  # queue for threading
    aqueue = MPQueue()  # for archiver

    ws = WSServer(port=Constants.wsport)
    ws.start()

    wd = WebServer(name='Flask')
    wd.start()

    serialReceiver: Dict[str, dict] = {
        'sGPS': {
            'port': '/dev/ttyACM0',
            'baud': 9600,
        },
        'sAIS': {
            'port': '/dev/ttyUSB0',
            'baud': 38400,
        },
    }
    for k, v in serialReceiver.items():
        receiver = Receiver(port=v['port'], baud=v['baud'], mailpost=mpqueue, name=k)
        if receiver.ready:
            receiver.start()

    udpReceiver: Dict[str, dict] = {
        'uGPS': {
            'port': 60001,
            'ipv4': '239.192.0.1',
        },
        'uAIS': {
            'port': 60008,
            'ipv4': '239.192.0.8',
        },
    }
    for k, v in udpReceiver.items():
        receiver = UDPListner(mailpost=mpqueue, port=v['port'], ipv4=v['ipv4'], name=k)
        receiver.start()

    archiver = Archive(qp=aqueue)
    archiver.start()

    session = Session(entrance=threadqueue, aq=aqueue)
    session.start()

    # setproctitle.setproctitle(current_process().name)
    setproctitle.setproctitle('EE:Main')

    while True:
        sentence = mpqueue.get()
        threadqueue.put(sentence)

