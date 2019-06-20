import os
import time
import psutil
import json
from threading import Thread


class HealthReport(Thread):

    def __init__(self, *, pid: int):

        super().__init__()

        self.daemon = True
        self.name = 'Secretary'

        self.p = psutil.Process(pid)
        self.last = {}

        # for c in self.p.children():
        #     print('Process %d = %s %f' % (c.pid, c.cmdline(), c.cpu_percent(interval=0.1)))
        #
        # print('OK')

    def run(self):

        while True:

            time.sleep(5)

            cpu = self.p.cpu_percent(interval=0.1)
            mem = self.p.memory_percent()

            info = {
                'mode': 'info',
                'cpu': round(cpu),
                'mem': round(mem),
            }
            if info != self.last:
                print('Main = %s' % info)
                self.last = info


if __name__ == '__main__':

    secretary = HealthReport(pid=2823)
    secretary.start()

    while True:
        time.sleep(1)