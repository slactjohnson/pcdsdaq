from threading import Thread, Event
import logging
import random

import numpy as np

connect_success = True
logger = logging.getLogger(__name__)


def connect(ami_str):
    logger.debug('simulated pyami connect')
    if not connect_success:
        raise RuntimeError('simulated fail')
    else:
        Entry._connected = True


class Entry:
    _connected = False

    def __init__(self, ami_name, ami_type, filter_string=None):
        logger.debug('Initializing test pyami Entry %s', ami_name)
        self._ami_name = ami_name
        self._run = Event()
        if not connect_success:
            raise RuntimeError('simulated fail: bad connection')
        if not Entry._connected:
            raise RuntimeError('simulated fail: did not call connect')
        self._filt = filter_string
        self._count = 0
        self._values = []
        Thread(target=self._count_thread, args=()).start()

    def _count_thread(self):
        logger.debug('Starting to collect test pyami values for %s',
                     self._ami_name)
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
        logger.debug('Clearing test pyami queue for %s', self._ami_name)
        self._values.clear()
