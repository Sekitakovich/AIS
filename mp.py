import time
from multiprocessing import Process
from multiprocessing import Queue


class Child(Process):

    def __init__(self, *, qp: Queue):
        super().__init__()
        self.qp = qp

    def run(self):
        while True:
            self.qp.put('Why?')
            time.sleep(3)


if __name__ == '__main__':

    qp = Queue()
    c = Child(qp=qp)
    c.start()

    while True:
        ooo = qp.get()
        print(ooo)
