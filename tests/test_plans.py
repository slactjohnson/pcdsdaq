import time
import logging

import pytest
from bluesky.plans import scan
from bluesky.plan_stubs import (trigger_and_read,
                                create, read, save, null)
from bluesky.preprocessors import run_decorator, run_wrapper

from pcdsdaq.plans import (daq_wrapper, daq_decorator, calib_cycle,
                           calib_at_step)

logger = logging.getLogger(__name__)


def test_daq_fixtures(daq, RE):
    """
    Verify that the test setup looks correct
    """
    logger.debug('test_daq_fixtures')
    assert daq._RE == RE


@pytest.mark.timeout(10)
def test_scan_on(daq, RE, sig):
    """
    We expect that the daq object is usable in a bluesky plan in the 'on' mode.
    """
    logger.debug('test_scan_on')

    @daq_decorator(mode='on')
    @run_decorator()
    def plan(reader):
        yield from null()
        for i in range(10):
            assert daq.state == 'Running'
            yield from trigger_and_read([reader])
        assert daq.state == 'Running'
        yield from null()

    RE(plan(sig))
    assert daq.state == 'Configured'


@pytest.mark.timeout(10)
def test_scan_manual(daq, RE, sig):
    """
    We expect that we can manually request calib cycles at specific times
    """
    logger.debug('test_scan_manual')

    @daq_decorator(mode=1)
    @run_decorator()
    def plan(reader):
        for i in range(10):
            yield from calib_cycle(events=1)
            assert daq.state == 'Open'
        assert daq.state == 'Open'

    RE(plan(sig))
    assert daq.state == 'Configured'


@pytest.mark.timeout(10)
def test_scan_auto(daq, RE, sig):
    """
    We expect that we can automatically get daq runs between create and save
    messages
    """
    logger.debug('test_scan_auto')

    @daq_decorator()
    @run_decorator()
    def plan(reader):
        logger.debug(daq.config)
        for i in range(10):
            yield from create()
            assert daq.state == 'Running'
            yield from read(reader)
            yield from save()
            assert daq.state == 'Open'

    daq.configure(mode='auto')
    RE(plan(sig))
    daq.configure(mode='auto', events=1)
    RE(plan(sig))
    assert daq.state == 'Configured'


@pytest.mark.timeout(10)
def test_scan_at_step(daq, RE, sig, mot):
    """
    We expect that calib_at_step works for the basic scan in manual mode
    """
    logger.debug(test_scan_at_step)

    dt = 1
    steps = 3
    daq_dur = steps * dt
    pos_end = 10
    start = time.time()
    RE(daq_wrapper(scan([sig], mot, 0, pos_end, steps,
                        per_step=calib_at_step(duration=dt)),
                   mode='manual'))
    end = time.time()
    duration = end - start
    assert daq_dur < duration < daq_dur + 1
    assert mot.position == pos_end


@pytest.mark.timeout(10)
def test_post_daq_RE(daq, RE, sig):
    """
    We expect that the RE will be clean after running with the daq
    """
    logger.debug('test_post_daq_RE')

    @run_decorator()
    def plan(reader, expected):
        for i in range(10):
            yield from create()
            assert daq.state == expected
            yield from read(reader)
            yield from save()

    RE(daq_wrapper(plan(sig, 'Running')))
    RE(plan(sig, 'Configured'))
    assert daq.state == 'Configured'


def test_bad_stuff(daq, RE):
    """
    Miscellaneous exception raises
    """
    logger.debug('test_bad_stuff')

    # daq wrapper cleanup with a bad plan
    def plan():
        yield from null()
        raise RuntimeError
    with pytest.raises(Exception):
        list(daq_wrapper(run_wrapper(plan)))
    assert daq._RE.msg_hook is None

    # calib_cycle at the wrong time
    def plan():
        yield from calib_cycle()
    with pytest.raises(RuntimeError):
        RE(plan())

    # calib_cycle with a bad config
    def plan():
        yield from calib_cycle()
    with pytest.raises(RuntimeError):
        RE(daq_wrapper(run_wrapper(plan())))


def test_inspect_calib_cycle():
    """
    Should be able to inspect this at all times
    """
    list(calib_cycle())
