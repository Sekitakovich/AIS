import logging
from queue import Queue
from multiprocessing import Queue as MPQueue
from typing import Dict, List

from session import Session
from receiver import Receiver
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

    wd = WebServer(name='Flask')
    wd.start()

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

    ws = WSServer(port=Constants.wsport)
    ws.start()

    for k, v in receiver.items():
        dst = Receiver(port=v['port'], baud=v['baud'], mailpost=mpqueue, name=k)
        dst.start()

    threadqueue = Queue()
    session = Session(entrance=threadqueue)
    session.start()

    # collector = Collector(mailpost=mpqueue)
    # collector.start()

    udp = UDPListner(mailpost=mpqueue)
    udp.start()

    while True:
        try:
            sentence = mpqueue.get()
            threadqueue.put(sentence)
        except KeyboardInterrupt as e:
            logger.debug(msg=e)
            break

