from datetime import datetime as dt
from enum import IntEnum
import json


class Constants(object):

    wdport = 8080  # port number for httpd
    wsport = 9999  # port number for websocket

    intervalsecs = 60  # for timekeeper

    class MessageType(IntEnum):

        Type1 = 1
        Type2 = 2
        Type3 = 3
        Type4 = 4
        Type5 = 5
        Type6 = 6
        Type7 = 7
        Type8 = 8
        Type9 = 9
        Type10 = 10
        Type11 = 11
        Type12 = 12
        Type13 = 13
        Type14 = 14
        Type15 = 15
        Type16 = 16
        Type17 = 17
        Type18 = 18
        Type19 = 19
        Type20 = 20
        Type21 = 21
        Type22 = 22
        Type23 = 23
        Type24 = 24
        Type25 = 25
        Type26 = 26
        Type27 = 27

    class Expire(object):

        static = 60 * 60
