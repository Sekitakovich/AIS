import time
import pigpio


class MonoLED(object):

    def __init__(self, *, bcm: int):
        self.pin = bcm

        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin, pigpio.OUTPUT)

        return

    def on(self):
        self.pi.write(self.pin, pigpio.HIGH)
        return

    def off(self):
        self.pi.write(self.pin, pigpio.LOW)
        return

    def __del__(self):
        self.pi.stop()
        return


if __name__ == '__main__':

    print('Start')

    led = MonoLED(bcm=21)

    for counter in range(5):
        try:
            led.on()
            time.sleep(1.0)
            led.off()
            time.sleep(0.5)
        except (KeyboardInterrupt,) as e:
            print(e)
            break

    led.off()
    print('End')
