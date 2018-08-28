import logging
import time
from importlib import import_module
from threading import Thread

from ophyd.device import Device, Component as Cpt
from ophyd.signal import AttributeSignal
from ophyd.status import Status
from ophyd.utils.errors import ReadOnlyError
from toolz.itertoolz import partition

logger = logging.getLogger(__name__)
pyami = None
pyami_connected = False
ami_proxy = None
l3t_file = None


def ensure_pyami():
    if pyami is None:
        logger.debug('importing pyami')
        globals()['pyami'] = import_module('pyami')
    if not pyami_connected:
        logger.debug('initializing pyami')
        try:
            if ami_proxy is None:
                raise RuntimeError('Must configure proxy with set_pyami_proxy')
            else:
                pyami.connect(ami_proxy)
                globals()['pyami_connected'] = True
        except Exception:
            globals()['pyami_connected'] = False
            raise


def set_pyami_proxy(proxy):
    globals()['ami_proxy'] = proxy


def set_l3t_file(l3t_file):
    globals()['l3t_file'] = l3t_file


def set_pyami_filter(*args, event_codes=None):
    filter_strings = []
    for det, lower, upper in partition(3, args):
        filter_strings.append(create_filter(det.prefix, lower, upper))
    if event_codes is not None:
        for code in event_codes:
            ami_name = 'DAQ:EVR:Evt{}'.format(code)
            filter_strings.append(create_filter(ami_name, 0.1, 2))
    if len(filter_strings) == 0:
        pyami.clear_l3t()
    else:
        if l3t_file is None:
            raise RuntimeError('Must configure l3t_file with set_l3t_file')
        final_filter = concat_filter_strings(filter_strings)
        pyami.set_l3t(final_filter, l3t_file)


def create_filter(ami_name, lower, upper):
    return '{}<{}<{}'.format(lower, ami_name, upper)


def concat_filter_strings(filter_strings, operator='|'):
    if len(filter_strings) == 0:
        raise ValueError('filter_strings must have at least one element')
    elif len(filter_strings) == 1:
        return filter_strings[0]
    else:
        sep = ')' + operator + '('
        return '(' + sep.join(filter_strings) + ')'


class AmiDet(Device):
    """
    Detector that gets data from pyami
    """
    mean = Cpt(AttributeSignal, attr='pyami_mean', kind='hinted')
    rms = Cpt(AttributeSignal, attr='pyami_rms', kind='omitted')
    err = Cpt(AttributeSignal, attr='pyami_err', kind='omitted')
    entries = Cpt(AttributeSignal, attr='pyami_entries', kind='normal')

    def __init__(self, prefix, *, name, filter_string=False, min_duration=0):
        ensure_pyami()
        self._entry = None
        self.filter_string = filter_string
        self.min_duration = min_duration
        self.pyami_mean = 0.
        self.pyami_rms = 0.
        self.pyami_err = 0.
        self.pyami_entries = 0
        super().__init__(prefix, name=name)

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
        self._get_data(del_entry=False)
        return super().get(*args, **kwargs)

    def read(self, *args, **kwargs):
        self._get_data(del_entry=True)
        return super().read(*args, **kwargs)

    def _get_data(self, del_entry):
        if self._entry is not None:
            data = self._entry.get()
            self.pyami_mean = data['mean']
            self.pyami_rms = data['rms']
            self.pyami_err = data['err']
            self.pyami_entries = data['entries']
            if del_entry:
                self._entry = None

    def put(self, *args, **kwargs):
        raise ReadOnlyError('AmiDet is read-only')
