import logging
import time
from importlib import import_module
from threading import Thread

from ophyd.device import Device, Component as Cpt
from ophyd.signal import AttributeSignal
from ophyd.status import Status
from ophyd.utils.errors import ReadOnlyError

logger = logging.getLogger(__name__)
pyami = None
pyami_connected = False
ami_proxy = None


def set_pyami_proxy(proxy):
    globals()['ami_proxy'] = proxy


class AmiDet(Device):
    """
    Detector that gets data from pyami
    """
    mean = Cpt(AttributeSignal, attr='pyami_mean', kind='hinted')
    rms = Cpt(AttributeSignal, attr='pyami_rms', kind='normal')
    err = Cpt(AttributeSignal, attr='pyami_err', kind='normal')
    entries = Cpt(AttributeSignal, attr='pyami_entries', kind='normal')

    def __init__(self, prefix, *, name, filter_string=False, min_duration=0):
        if pyami is None:
            globals()['pyami'] = import_module('pyami')
        if not pyami_connected:
            self._connect_pyami()
        self._entry = None
        self.filter_string = filter_string
        self.min_duration = min_duration
        self.pyami_mean = 0.
        self.pyami_rms = 0.
        self.pyami_err = 0.
        self.pyami_entries = 0
        super().__init__(prefix, name=name)

    def _connect_pyami(self):
        logger.debug('Initializing pyami')
        try:
            if ami_proxy is None:
                raise RuntimeError('Must configure proxy with set_pyami_proxy')
            else:
                pyami.connect(ami_proxy)
                globals()['pyami_connected'] = True
        except Exception:
            globals()['pyami_connected'] = False
            raise

    def trigger(self):
        if self.filter_string:
            self._entry = pyami.Entry(self.prefix, 'Scalar',
                                      self.filter_string)
        else:
            self._entry = pyami.Entry(self.prefix, 'Scalar')
        if self.min_duration:
            def inner(duration, status):
                time.sleep(duration)
                status._finished()
            status = Status(obj=self)
            Thread(target=inner, args=(self.min_duration, status)).start()
            return status
        else:
            return Status(obj=self, done=True, success=True)

    def get(self, *args, **kwargs):
        self._get_data()
        return super().get(*args, **kwargs)

    def _get_data(self):
        if self._entry is not None:
            data = self._entry.get()
            self.pyami_mean = data['mean']
            self.pyami_rms = data['rms']
            self.pyami_err = data['err']
            self.pyami_entries = data['entries']
            self._entry = None

    def put(self, *args, **kwargs):
        raise ReadOnlyError('AmiDet is read-only')
