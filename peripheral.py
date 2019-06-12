from threading import Thread
import time
import pigpio


class MonoLED(object):

    def __init__(self, *, bcm: int):
        self.pin = bcm

        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin, pigpio.OUTPUT)

        self.idle = 'IDLE'
        self.slow = 'SLOW'
        self.middle = 'MIDDLE'
        self.fast = 'FAST'
        self.stop = ''

        self.table = {
            self.idle: {
                'on': 0.05,
                'off': 2.5,
            },
            self.slow: {
                'on': 0.1,
                'off': 1.0,
            },
            self.middle: {
                'on': 1.0,
                'off': 0.5,
            },
            self.fast: {
                'on': 0.25,
                'off': 0.25,
            },
        }
        self.mode: str = self.stop

        self.ooo = Thread(target=self.run)
        self.ooo.start()

        return

    def on(self):
        self.pi.write(self.pin, pigpio.HIGH)
        return

    def off(self):
        self.pi.write(self.pin, pigpio.LOW)
        return

    def set(self, *, mode: str = 'SLOW'):

        self.mode = mode

        return

    def run(self):

        while True:

            if self.mode:
                pattern = self.table[self.mode]
                self.on()
                time.sleep(pattern['on'])
                self.off()
                time.sleep(pattern['off'])
                pass
            else:
                time.sleep(1)

    def __del__(self):
        self.pi.stop()
        return


if __name__ == '__main__':

    print('Start')

    led = MonoLED(bcm=21)

    led.set(mode=led.fast)

    time.sleep(10)

    print('End')
