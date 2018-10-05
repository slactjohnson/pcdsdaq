import logging
import random

import numpy as np

connect_success = True
logger = logging.getLogger(__name__)

set_l3t_count = 0
clear_l3t_count = 0


def connect(ami_str):
    logger.debug('simulated pyami connect')
    if not connect_success:
        raise RuntimeError('simulated fail')
    else:
        Entry._connected = True


def set_l3t(filter_string, l3t_file):
    global set_l3t_count
    set_l3t_count += 1


def clear_l3t():
    global clear_l3t_count
    clear_l3t_count += 1


class Entry:
    _connected = False

    def __init__(self, ami_name, ami_type, filter_string=None):
        logger.debug('Initializing test pyami Entry %s', ami_name)
        self._ami_name = ami_name
        if not connect_success:
            raise RuntimeError('simulated fail: bad connection')
        if not Entry._connected:
            raise RuntimeError('simulated fail: did not call connect')
        self._filt = filter_string
        self.clear()

    def get(self):
        if len(self._values):
            return dict(mean=np.mean(self._values),
                        rms=np.std(self._values),
                        entries=len(self._values))
        else:
            return dict(mean=0, rms=0, entries=0)

    def clear(self):
        self._count = random.randint(1, 100)
        self._values = [random.random() for i in range(self._count)]
