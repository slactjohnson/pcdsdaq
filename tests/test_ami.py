import logging

import pytest

from bluesky.callbacks import collector
from bluesky.plans import count

import pcdsdaq.ami
import pcdsdaq.sim.pyami as sim_pyami
from pcdsdaq.ami import (AmiDet, set_pyami_proxy, set_l3t_file,
                         set_pyami_filter, concat_filter_strings)

logger = logging.getLogger(__name__)


def test_ami_basic(ami):
    logger.debug('test_ami_basic')
    ami.trigger()
    stats = ami.get()
    assert stats.entries > 0


def test_ami_scan(ami, RE):
    logger.debug('test_ami_scan')
    ami.min_duration = 1
    ami.filter_string = '4<x<5'
    mean_list = []
    coll = collector(ami.mean.name, mean_list)
    num = 5
    RE(count([ami], num=num), {'event': coll})
    assert len(mean_list) == num


def test_ami_errors(ami):
    logger.debug('test_ami_errors')
    with pytest.raises(Exception):
        ami.put(4)
    set_pyami_proxy(None)
    pcdsdaq.ami.pyami_connected = False
    with pytest.raises(Exception):
        AmiDet('NOPROXY', name='noproxy')
    set_pyami_proxy('tst')
    sim_pyami.connect_success = False
    with pytest.raises(Exception):
        AmiDet('NOCONN', name='noconn')


def test_no_pyami():
    logger.debug('test_no_pyami')
    pcdsdaq.ami.pyami = None
    with pytest.raises(ImportError):
        AmiDet('NOPYAMI', name='nopyami')


def test_set_pyami_filter_clear(ami):
    logger.debug('test_set_pyami_filter_clear')
    set_pyami_filter()
    assert sim_pyami.clear_l3t_count == 1


def test_set_pyami_filter_one(ami):
    logger.debug('test_set_pyami_filter_one')
    set_pyami_filter(ami, 0, 1)
    assert sim_pyami.set_l3t_count == 1


def test_set_pyami_filter_two(ami):
    logger.debug('test_set_pyami_filter_two')
    set_pyami_filter(ami, 0, 1, ami, 2, 3)
    assert sim_pyami.set_l3t_count == 1


def test_set_pyami_filter_evr(ami):
    logger.debug('test_set_pyami_filter_evr')
    set_pyami_filter(event_codes=[162, 163])
    assert sim_pyami.set_l3t_count == 1


def test_set_pyami_filter_all(ami):
    logger.debug('test_set_pyami_filter_all')
    set_pyami_filter(ami, 0, 1, ami, 2, 3, event_codes=[162, 163])
    assert sim_pyami.set_l3t_count == 1


def test_set_pyami_filter_error(ami):
    logger.debug('test_set_pyami_filter_error')
    set_l3t_file(None)
    with pytest.raises(Exception):
        set_pyami_filter(event_codes=[21])


def test_set_pyami_filter_daq(daq, ami):
    logger.debug('test_set_pyami_filter_daq')
    daq.set_filter()
    assert sim_pyami.clear_l3t_count == 1


def test_concat_error():
    logger.debug('test_concat_error')
    with pytest.raises(Exception):
        concat_filter_strings([])
