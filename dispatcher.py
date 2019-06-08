import logging
from threading import Lock
from typing import List
from typing import Dict

from resultbox import ResultBox
from Payloads.header import Structure as Header
from Payloads.type1to3 import Structure as Type1to3
from Payloads.type4and11 import Structure as Type4and11
from Payloads.type5 import Structure as Type5
from Payloads.type6 import Structure as Type6
from Payloads.type7and13 import Structure as Type7and13
from Payloads.type8 import Structure as Type8
from Payloads.type12 import Structure as Type12
from Payloads.type14 import Structure as Type14
from Payloads.type15 import Structure as Type15
from Payloads.type16 import Structure as Type16
from Payloads.type17 import Structure as Type17
from Payloads.type18 import Structure as Type18
from Payloads.type19 import Structure as Type19
from Payloads.type20 import Structure as Type20
from Payloads.type21 import Structure as Type21
from Payloads.type24A import Structure as Type24A
from Payloads.type24B import Structure as Type24B
from Payloads.type27 import Structure as Type27

from common import Constants
from vessel import Vessel


class Dispatcher(object):

    def __init__(self):

        self.logger = logging.getLogger('Log')

        self.vessel: Dict[int, Vessel] = {}

        self.header = Header()
        self.type1to3 = Type1to3()
        self.type4and11 = Type4and11()
        self.type5 = Type5()
        self.type6 = Type6()
        self.type7and13 = Type7and13()
        self.type8 = Type8()
        self.type12 = Type12()
        self.type14 = Type14()
        self.type15 = Type15()
        self.type16 = Type16()
        self.type17 = Type17()
        self.type18 = Type18()
        self.type19 = Type19()
        self.type20 = Type20()
        self.type21 = Type21()
        self.type24A = Type24A()
        self.type24B = Type24B()
        self.type27 = Type27()

        self.save24 = {}

    def parse(self, *, payload: str, fillbits: int = 0) -> ResultBox:

        rb = ResultBox()

        header = self.header.decode(payload=payload)
        if header.error == header.ErrorCode.noError:

            body = ResultBox()
            
            rb.member['header'] = header.member

            thisType: int = int(header.member['type'])
            thisRepeat: int = int(header.member['repeat'])
            thisMMSI: int = int(header.member['mmsi'])

            if thisType in (Constants.MessageType.Type1, Constants.MessageType.Type2, Constants.MessageType.Type3):
                body = self.type1to3.decode(payload=payload)
                if body.error == body.ErrorCode.noError:
                    src = body.member
                    if thisMMSI not in self.vessel:
                        self.vessel[thisMMSI] = Vessel()
                    self.vessel[thisMMSI].updateDynamic(
                        lat=src['maplat'],
                        lng=src['maplng'],
                        sog=src['speed'],
                        cog=src['course'])

                pass

            elif thisType in (Constants.MessageType.Type4, Constants.MessageType.Type11):
                body = self.type4and11.decode(payload=payload)
                pass

            elif thisType == Constants.MessageType.Type5:
                body = self.type5.decode(payload=payload)
                if body.error == body.ErrorCode.noError:
                    src = body.member
                    if thisMMSI not in self.vessel:
                        self.vessel[thisMMSI] = Vessel()
                    self.vessel[thisMMSI].updateStatic(
                        version=src['ais_version'],
                        imo=src['imo'],
                        name=src['shipname'],
                        type=src['shiptype'],
                        callsign=src['callsign'],
                        aistype=Constants.AIStype.ClassA,
                    )
                pass

            elif thisType == Constants.MessageType.Type6:
                body = self.type6.decode(payload=payload)
                pass

            elif thisType in (Constants.MessageType.Type7, Constants.MessageType.Type13):
                body = self.type7and13.decode(payload=payload)
                pass

            elif thisType == Constants.MessageType.Type8:
                body = self.type8.decode(payload=payload)
                pass

            elif thisType == Constants.MessageType.Type12:
                body = self.type12.decode(payload=payload)
                pass

            elif thisType == Constants.MessageType.Type14:
                body = self.type14.decode(payload=payload)
                pass

            elif thisType == Constants.MessageType.Type15:
                body = self.type15.decode(payload=payload)
                pass

            elif thisType == Constants.MessageType.Type16:
                body = self.type16.decode(payload=payload)
                pass

            elif thisType == Constants.MessageType.Type17:
                body = self.type17.decode(payload=payload)
                pass

            elif thisType == Constants.MessageType.Type18:
                body = self.type18.decode(payload=payload)
                if body.error == body.ErrorCode.noError:
                    src = body.member
                    if thisMMSI not in self.vessel:
                        self.vessel[thisMMSI] = Vessel()
                    self.vessel[thisMMSI].updateDynamic(
                        lat=src['maplat'],
                        lng=src['maplng'],
                        sog=src['speed'],
                        cog=src['course'])
                pass

            elif thisType == Constants.MessageType.Type19:
                body = self.type19.decode(payload=payload)
                if body.error == body.ErrorCode.noError:
                    src = body.member
                    if thisMMSI not in self.vessel:
                        self.vessel[thisMMSI] = Vessel()
                    self.vessel[thisMMSI].updateStatic(
                        name=src['shipname'],
                        type=src['shiptype'],
                        aistype=Constants.AIStype.ClassB_SOTDMA,
                    )
                    self.vessel[thisMMSI].updateDynamic(
                        lat=src['maplat'],
                        lng=src['maplng'],
                        sog=src['speed'],
                        cog=src['course'])
                pass

            elif thisType == Constants.MessageType.Type20:
                body = self.type20.decode(payload=payload)
                pass

            elif thisType == Constants.MessageType.Type21:
                body = self.type21.decode(payload=payload)
                pass

            elif thisType == Constants.MessageType.Type24:

                if thisMMSI not in self.save24:
                    self.save24[thisMMSI] = {}

                target = self.save24[thisMMSI]

                partA = self.type24A.decode(payload=payload)
                if partA.error == partA.ErrorCode.noError:
                    if partA.member['partno'] == 0:
                        target['A'] = partA
                partB = self.type24B.decode(payload=payload)
                if partB.error == partB.ErrorCode.noError:
                    if partB.member['partno'] == 1:
                        target['B'] = partB

                if 'A' in target and 'B' in target:
                    result = target['A']
                    result.member.update(target['B'].member)
                    body = result
                    src = body.member
                    if thisMMSI not in self.vessel:
                        self.vessel[thisMMSI] = Vessel()
                    self.vessel[thisMMSI].updateStatic(
                        name=src['shipname'],
                        type=src['shiptype'],
                        callsign=src['callsign'],
                        aistype=Constants.AIStype.ClassB_CSTDMA,
                    )
                    pass
                else:
                    body.error = rb.ErrorCode.AIS.type24notCompleted
                    pass

            elif thisType == Constants.MessageType.Type27:
                body = self.type27.decode(payload=payload)
                pass

            elif thisType in (9, 10, 22, 23, 25, 26):
                self.logger.debug(msg='--- not supported %d' % thisType)
                body.error = body.ErrorCode.AIS.unsupportedType

            else:
                body.error = body.ErrorCode.AIS.unknownType

            if body.error == body.ErrorCode.noError:
                rb.member['body'] = body.member
            else:
                rb.error = body.error

            if thisMMSI == 0:
                # self.logger.debug(msg='found zero MMSI at [%s] [%s]' % (header.member, body.member,))
                pass

            if thisRepeat != 0:
                pass
                # self.logger.debug(msg='found repeater at [%s]' % (str(header),))

        else:
            rb.error = header.error

        # for k, v in self.vessel.items():
        #     if v.aisType in (Constants.AIStype.ClassB_SOTDMA, Constants.AIStype.ClassB_CSTDMA):
        #         print(v)

        return rb
