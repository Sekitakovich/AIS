import logging
from queue import Queue as ThreadQueue
from multiprocessing import Queue as MPQueue
from typing import Dict, List

from session import Session
from serialreceiver import Receiver
from webserver import Server as WebServer
from wsserver import Server as WSServer
from common import Constants
from udplistner import Receiver as UDPListner


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

    ws = WSServer(port=Constants.wsport)
    ws.start()

    wd = WebServer(name='Flask')
    wd.start()

    serialReceiver: Dict[str, dict] = {
        # 'GPS': {
        #     'port': '/dev/ttyACM0',
        #     'baud': 9600,
        # },
        'AIS': {
            'port': '/dev/ttyUSB0',
            'baud': 38400,
        },
    }
    for k, v in serialReceiver.items():
        receiver = Receiver(port=v['port'], baud=v['baud'], mailpost=mpqueue, name=k)
        receiver.start()

    udpReceiver: Dict[str, dict] = {
        'GPS': {
            'port': 60001,
            'ipv4': '239.192.0.1',
        },
        'AIS': {
            'port': 60008,
            'ipv4': '239.192.0.8',
        },
    }
    for k, v in udpReceiver.items():
        receiver = UDPListner(mailpost=mpqueue, port=v['port'], ipv4=v['ipv4'])
        receiver.start()

    session = Session(entrance=threadqueue)
    session.start()

    while True:
        try:
            sentence = mpqueue.get()
            threadqueue.put(sentence)
        except KeyboardInterrupt as e:
            logger.debug(msg=e)
            break

