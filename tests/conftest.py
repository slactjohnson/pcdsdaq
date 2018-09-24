from bluesky import RunEngine
from ophyd.sim import SynSignal, motor1

import pcdsdaq.sim.pyami as sim_pyami
import pcdsdaq.sim.pydaq as sim_pydaq
from pcdsdaq.ami import AmiDet, set_pyami_proxy, set_l3t_file
from pcdsdaq.daq import Daq
from pcdsdaq.sim import set_sim_mode
from pcdsdaq.sim.pydaq import SimNoDaq

import pytest


@pytest.fixture(scope='function')
def sim():
    set_sim_mode(True)


@pytest.fixture(scope='function')
def nosim():
    set_sim_mode(False)


@pytest.fixture(scope='function')
def daq(RE, sim):
    sim_pydaq.conn_err = None
    return Daq(RE=RE, platform=0)


@pytest.fixture(scope='function')
def nodaq(RE):
    return SimNoDaq(RE=RE)


@pytest.fixture(scope='function')
def ami_det(sim):
    set_pyami_proxy('tstproxy')
    set_l3t_file('tstfile')
    sim_pyami.connect_success = True
    sim_pyami.set_l3t_count = 0
    sim_pyami.clear_l3t_count = 0
    return AmiDet('TST', name='test')


@pytest.fixture(scope='function')
def RE():
    RE = RunEngine({})
    RE.verbose = True
    return RE


@pytest.fixture(scope='function')
def sig():
    sig = SynSignal(name='test')
    sig.put(0)
    return sig


@pytest.fixture(scope='function')
def mot():
    motor1.set(0)
    return motor1
