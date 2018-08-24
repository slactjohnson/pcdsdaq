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


def set_pyami_proxy(proxy):
    AmiDet.proxy = proxy


class AmiDet(Device):
    """
    Detector that gets data from pyami
    """
    proxy = None

    mean = Cpt(AttributeSignal, attr='pyami_mean', kind='hinted')
    rms = Cpt(AttributeSignal, attr='pyami_rms', kind='normal')
    err = Cpt(AttributeSignal, attr='pyami_err', kind='normal')
    entries = Cpt(AttributeSignal, attr='pyami_entries', kind='normal')

    def __init__(self, prefix, *, name, filter_string=False, min_duration=0):
        if pyami is None:
            self._connect_pyami()
        self._entry = None
        self.filter_string = filter_string
        self.min_duration = min_duration
        self.pyami_mean = None
        self.pyami_rms = None
        self.pyami_err = None
        self.pyami_entries = None
        super().__init__(prefix, name=name)

    def _connect_pyami(self):
        globals()['pyami'] = import_module('pyami')
        try:
            if self.proxy is None:
                raise RuntimeError('Must configure proxy with set_pyami_proxy')
            else:
                pyami.connect(self.proxy)
        except Exception:
            globals()['pyami'] = None
            raise

    def trigger(self):
        if self.filter_string:
            self._entry = pyami.Entry(self.ami_name, 'Scalar',
                                      self.filter_string)
        else:
            self._entry = pyami.Entry(self.ami_name, 'Scalar')
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
