"""
This module provides a simulated pydaq module for offline testing and training.
It does not assume that the real pydaq module is available.
"""
from importlib import import_module

import pcdsdaq.daq as daq
from . import pydaq


def set_sim_mode(sim_mode):
    """
    Parameters
    ----------
    sim_mode: bool
        If True, we'll set the Daq class to run in simulated mode. If False,
        we'll attempt to import pydaq to run the Daq in real mode.
    """
    if sim_mode:
        daq.pydaq = pydaq
    else:
        real_pydaq = import_module('pydaq')
        daq.pydaq = real_pydaq
