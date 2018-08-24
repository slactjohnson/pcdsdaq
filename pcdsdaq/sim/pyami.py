from threading import Thread, Event
import random

import numpy as np

connect_success = True


def connect(ami_str):
    if not connect_success:
        raise RuntimeError('simulated fail')
    else:
        Entry._connected = True


class Entry:
    _connected = False

    def __init__(self, ami_name, ami_type, filter_string=None):
        if not connect_success or not self._connected:
            raise RuntimeError('simulated fail')
        self._filt = filter_string
        self._run = Event()
        self._count = 0
        self._values = []
        Thread(target=self._count_thread, args=()).start()

    def _count_thread(self):
        while not self._run.wait(0.1):
            self._values.append(random.random())
            self._count += 1

    def __del__(self):
        self._run.set()

    def get(self):
        return dict(mean=np.mean(self._values),
                    rms=np.sqrt(np.mean(np.square(self._values))),
                    err=0,
                    entries=len(self._values))

    def clear(self):
        self._values.clear()
