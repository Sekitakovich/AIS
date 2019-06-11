import time
from typing import Dict, List
from threading import Thread
from threading import Event

import pigpio


class KeyNote(object):

    def __init__(self, *, hz: int, length: float):
        self.hz = hz
        self.length = length


class Jingle(object):

    def __init__(self, *, pattern: List[KeyNote], loop: bool = False):
        self.loop: bool = loop
        self.pattern = pattern

        return


class Buzzer(object):

    def __init__(self, *, bcm: int):
        self.pin = bcm

        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin, pigpio.OUTPUT)

        self.jingle: Dict[str, Jingle] = {
            'pipo': Jingle(loop=False, pattern=[
                KeyNote(hz=2000, length=0.1),
                KeyNote(hz=1000, length=0.2),
                KeyNote(hz=0, length=0.5),
            ]),
            'popi': Jingle(loop=False, pattern=[
                KeyNote(hz=1000, length=0.1),
                KeyNote(hz=2000, length=0.2),
                KeyNote(hz=0, length=0.5),
            ]),
            'pupu': Jingle(loop=False, pattern=[
                KeyNote(hz=1000, length=0.1),
                KeyNote(hz=0, length=0.05),
                KeyNote(hz=1000, length=0.1),
                KeyNote(hz=0, length=0.05),
                KeyNote(hz=0, length=0.5),
            ]),
            'sos': Jingle(loop=True, pattern=[
                KeyNote(hz=440, length=0.1),
                KeyNote(hz=0, length=0.1),
                KeyNote(hz=440, length=0.1),
                KeyNote(hz=0, length=0.1),
                KeyNote(hz=440, length=0.1),
                KeyNote(hz=0, length=0.1),
                KeyNote(hz=440, length=0.3),
                KeyNote(hz=0, length=0.1),
                KeyNote(hz=440, length=0.3),
                KeyNote(hz=0, length=0.1),
                KeyNote(hz=440, length=0.3),
                KeyNote(hz=0, length=0.1),
                KeyNote(hz=0, length=0.5),
            ]),
        }
        self.current: str = ''
        self.event = Event()
        self.speaker = Thread(target=self.play, daemon=True)
        self.speaker.start()

    def play(self):

        while True:
            if self.current:
                jingle = self.jingle[self.current]
                print('Playing [%s] loop = %s' % (self.current, jingle.loop))
                for sound in jingle.pattern:
                    self.pi.hardware_PWM(self.pin, sound.hz, 100000)
                    time.sleep(sound.length)

                self.pi.hardware_PWM(self.pin, 0, 0)
                if not jingle.loop:
                    self.current = ''
                pass
            else:
                print('Waiting ...')
                self.event.wait()
                self.event.clear()

    def push(self, *, name: str):

        self.current = name
        self.event.set()
        return

    def off(self):

        self.current = ''
        self.pi.hardware_PWM(self.pin, 0, 0)
        return


if __name__ == '__main__':

    print('Start')

    buzzer = Buzzer(bcm=18)

    time.sleep(3)
    buzzer.push(name='sos')

    time.sleep(3)
    buzzer.push(name='pipo')

    time.sleep(3)
    buzzer.push(name='popi')

    time.sleep(3)
    buzzer.off()

    print('End')
