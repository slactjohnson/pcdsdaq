from bluesky import RunEngine
from ophyd.sim import SynSignal, motor1

import pcdsdaq.sim.pydaq as sim_pydaq
from pcdsdaq.daq import Daq
from pcdsdaq.sim import set_sim_mode
from pcdsdaq.sim.pydaq import SimNoDaq

import pytest


@pytest.fixture(scope='function')
def daq(RE):
    set_sim_mode(True)
    sim_pydaq.conn_err = None
    daq = Daq(RE=RE, platform=0)
    yield daq
    try:
        # Sim daq can freeze pytest's exit if we don't end the run
        daq.end_run()
    except Exception:
        pass


@pytest.fixture(scope='function')
def nodaq(RE):
    return SimNoDaq(RE=RE)


@pytest.fixture(scope='function')
def nosim():
    set_sim_mode(False)


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
