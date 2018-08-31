import logging
import time
from importlib import import_module
from threading import Thread

from ophyd.device import Device, Component as Cpt
from ophyd.signal import Signal
from ophyd.status import Status
from ophyd.utils.errors import ReadOnlyError
from toolz.itertoolz import partition

logger = logging.getLogger(__name__)
pyami = None
pyami_connected = False
ami_proxy = None
l3t_file = None


def ensure_pyami():
    """
    Makes sure pyami is imported and connected

    This requires set_pyami_proxy to be called first.

    This will be called the first time pyami is needed. We don't import at the
    top of this file because we need to be able to import this file even if
    pyami isn't in the environment, which is semi-frequent.
    """
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
    """
    Pick the hostname or group to use for the pyami connection.

    Parameters
    ----------
    proxy: ``str`` or ``int``
        Either the server name or group number
    """
    globals()['ami_proxy'] = proxy


def set_l3t_file(l3t_file):
    """
    Pick the file to write out for the l3t trigger

    Parameters
    ----------
    l3t_file: ``str``
        Full file path
    """
    globals()['l3t_file'] = l3t_file


def set_pyami_filter(*args, event_codes=None, operator='&'):
    """
    Set up the l3t filters.

    These connect through pyami to call set_l3t or clear_l3t. The function
    takes in arbitrary dets whose prefixes are the ami names, along with low
    and highs.

    Event codes are handled as a special case, since you always want high vs
    low.

    Parameters
    ----------
    *args: (``AmiDet``, ``float``, ``float``) n times
        A sequence of (detector, low, high), which create filters that make
        sure the detector is between low and high.

    event_codes: ``list``, optional
        A list of event codes to include in the filter. l3pass will be when the
        event code is present.

    operator: ``str``, optional
        The operator for combining the detector ranges and event codes. This
        can either be ``|`` to ``or`` the conditions together, so l3pass will
        happen if any filter passes, or it can be left at the default ``&`` to
        ``and`` the conditions together, so l3pass will only happen if all
        filters pass.
    """
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
    """
    Helper function for creating an ami filter string.

    Parameters
    ----------
    ami_name: ``str``
        The name of the value in ami

    lower: ``float``
        The lower bound for the value to pass

    upper: ``float``
        The upper bound for the value to pass
    """
    return '{}<{}<{}'.format(lower, ami_name, upper)


def concat_filter_strings(filter_strings, operator='&'):
    """
    Helper function to combine ami filter strings

    Parameters
    ----------
    filter_strings: ``list``
        The valid filter strings to combine

    operator: ``str``
        The operator to place between the filter strings. This can either be
        ``&`` or ``|``, for ``and`` or ``or`` respectively.
    """
    if len(filter_strings) == 0:
        raise ValueError('filter_strings must have at least one element')
    elif len(filter_strings) == 1:
        return filter_strings[0]
    else:
        sep = ')' + operator + '('
        return '(' + sep.join(filter_strings) + ')'


class AmiDet(Device):
    """
    Detector that gets data from pyami.

    This only supports scalars. The array features are known to crash both the
    python session and active ami clients, so don't use them.

    Parameters
    ----------
    prefix: ``str``
        The ami name to use to retrieve the data.

    name: ``str``, required keyword
        The shorter name to use to label the data.

    filter_str: ``str``, optional
        If provided, we'll filter the incoming data using this filter string.

    min_duration: ``float``, optional
        If provided, we'll wait this many seconds before declaring the
        acquisition as complete. Otherwise, we'll stop acquring on read.
    """
    mean = Cpt(Signal, kind='hinted', value=0.)
    rms = Cpt(Signal, kind='omitted', value=0.)
    err = Cpt(Signal, kind='omitted', value=0.)
    entries = Cpt(Signal, kind='normal', value=0)

    def __init__(self, prefix, *, name, filter_string=False, min_duration=0):
        ensure_pyami()
        self._entry = None
        self.filter_string = filter_string
        self.min_duration = min_duration
        super().__init__(prefix, name=name)

    def trigger(self):
        """
        Called during a bluesky scan to start taking ami data.

        If min_duration is zero, this will return a status already marked done
        and successful. Otherwise, this will return a status that will be
        marked done after min_duration seconds.

        Internally this creates a new pyami.Entry object. These objects start
        accumulating data immediatley.
        """
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
        """
        Can be called interactively to check the accumulated ami data.

        This will not stop the accumulation of data.
        """
        self._get_data(del_entry=False)
        return super().get(*args, **kwargs)

    def read(self, *args, **kwargs):
        """
        Called during a bluesky scan to get the accumulated ami data.

        This will stop the accumulation of data. We aggresively reset the data
        accumulation to avoid memory leaking.
        """
        self._get_data(del_entry=True)
        return super().read(*args, **kwargs)

    def _get_data(self, del_entry):
        """
        Helper function that stuffs ami data into this device's signals.

        Parameters
        ----------
        del_entry: ``bool``
            If ``True``, we'll clear the accumulated data after getting it.
        """
        if self._entry is not None:
            data = self._entry.get()
            self.mean.put(data['mean'])
            self.rms.put(data['rms'])
            self.err.put(data['err'])
            self.entries.put(data['entries'])
            if del_entry:
                self._entry = None

    def put(self, *args, **kwargs):
        raise ReadOnlyError('AmiDet is read-only')
