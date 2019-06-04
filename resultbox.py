import enum


class ResultBox(object):
    """
    Integrated functions interface standard class by K.Seki 2018

    use as follows

    rBox = xxx.func(args=args)
    if rBox.error = rBox.ErrorCode.noError:
        value = rBox.result .......
    """
    class ErrorCode(object):

        noError = 0
        fatal = 9999

        class NMEA(enum.Enum):
            badFormat = 1
            badSum = 2
            unknownType = 3
            badSymbol = 4
            blockTooShort = 5
            notFoundCRLF = 6
            memberNotFull = 7
            haveNoStar = 8
            haveNoHexCS = 9
            haveNoItem = 10
            tooManyStar = 11
            badLength = 12
            badBegin = 13

        class AIS(enum.Enum):

            badFormat = 1
            badCharFound = 2
            tooShort = 3
            unknownType = 4
            unsupportedType = 97
            type24notCompleted = 98
            noMMSI = 99

    def __init__(self, *, error=ErrorCode.noError):

        self.error = error
        self.member = {}
