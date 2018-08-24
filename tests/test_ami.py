import logging

import pytest

from bluesky.callbacks import collector
from bluesky.plans import count

import pcdsdaq.ami
import pcdsdaq.sim.pyami as sim_pyami
from pcdsdaq.ami import AmiDet, set_pyami_proxy

logger = logging.getLogger(__name__)


def test_ami_basic(ami):
    logger.debug('test_ami_basic')
    ami.trigger()
    stats = ami.read()
    assert ami.mean.name in stats
    assert stats[ami.entries.name]['value'] > 0


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
