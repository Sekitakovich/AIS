import time
from typing import Dict, List

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
            ]),
            'popi': Jingle(loop=False, pattern=[
                KeyNote(hz=1000, length=0.1),
                KeyNote(hz=2000, length=0.2),
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

    def play(self, *, name: str):

        jingle = self.jingle[name]

        while True:
            for sound in jingle.pattern:
                self.pi.hardware_PWM(self.pin, sound.hz, 100000)
                time.sleep(sound.length)

            if jingle.loop == False:
                break

        self.pi.hardware_PWM(self.pin, 0, 0)

        return

    def on(self):
        for hz in range(1000, 4000, 100):
            self.pi.hardware_PWM(self.pin, hz, 100000)
            time.sleep(0.005)
        self.pi.hardware_PWM(self.pin, 0, 0)
        return

    def off(self):
        self.pi.hardware_PWM(self.pin, 0, 0)
        return


if __name__ == '__main__':

    print('Start')

    buzzer = Buzzer(bcm=18)

    buzzer.play(name='pipo')

    for counter in range(5):
        try:
            time.sleep(1)
        except (KeyboardInterrupt,) as e:
            print(e)
            buzzer.play(name='pupu')
            break

    buzzer.play(name='popi')
    print('End')
