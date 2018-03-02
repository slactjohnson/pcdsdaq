=======
pcdsdaq
=======
.. image:: https://travis-ci.org/pcdshub/pcdsdaq.svg?branch=master
   :target: https://travis-ci.org/pcdshub/pcdsdaq
   :alt: Build Status
.. image:: https://codecov.io/gh/pcdshub/pcdsdaq/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/pcdshub/pcdsdaq
   :alt: Code Coverage

The pcdsdaq module provides a clean interface for user control of the LCLS1
DAQ through the LCLS1 DAQ's Python c libraries, ``pydaq``, ``pycdb``, and
``pyami``. It provides utilities for controlling DAQ runs and incorporating
the DAQ into ``bluesky`` plans.

Requirements
------------

- ``python`` >= 3.6
- ``bluesky`` >= 1.2.0
- ``pydaq``
- ``pycdb``
- ``pyami``
