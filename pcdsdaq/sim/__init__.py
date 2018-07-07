"""
This module provides a simulated pydaq module for offline testing and training.
It does not assume that the real pydaq module is available.
"""
import logging
from importlib import import_module

import pcdsdaq.daq as daq
import pcdsdaq.ext_scripts as ext
from . import pydaq

logger = logging.getLogger(__name__)


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
        ext.hutch_name = pydaq.sim_hutch_name
        ext.get_run_number = pydaq.sim_get_run_number
    else:
        try:
            real_pydaq = import_module('pydaq')
            daq.pydaq = real_pydaq
        except ImportError:
            logger.error('pydaq not available in this session')
        ext.hutch_name = pydaq.hutch_name
        ext.get_run_number = pydaq.get_run_number
