Using the DAQ with Bluesky
==========================
Some utilities are provided for running the daq in sync with a ``bluesky``
``plan``. This document will assume some familiarity with ``bluesky`` and
how to use the ``RunEngine``, but does not require a full understanding of
the internals.

I am going to introduce these through a series of examples. You can check the
full `api docs <./plans_api>` for more information.

Creating a Daq object with the RunEngine
----------------------------------------
The `Daq` needs to register a ``RunEngine`` instance for this to work. This
must be the same ``RunEngine`` that will be running all of the plans.

.. code-block:: python

    from bluesky import RunEngine
    from pcdsdaq.daq import Daq
    from pcdsdaq.sim import set_sim_mode

    set_sim_mode(True)
    RE = RunEngine({})
    daq = Daq(RE=RE)


.. ipython:: python
    :suppress:

    from bluesky import RunEngine
    from ophyd.sim import motor1
    from ophyd.sim import det1
    from pcdsdaq.daq import Daq
    from pcdsdaq.sim import set_sim_mode

    set_sim_mode(True)
    RE = RunEngine({})
    daq = Daq(RE=RE)


Basic Plan with Daq Support
---------------------------
The simplest way to include the daq is to turn it on at the start of the plan
and turn it off at the end of the plan. This is done using the `daq_wrapper`
or `daq_decorator`.

.. code-block:: python

    from bluesky.plan_stubs import mv
    from bluesky.preprocessors import run_decorator
    from pcdsdaq.plans import daq_decorator

    @daq_decorator()
    @run_decorator()
    def basic_plan(motor, start, end):
        yield from mv(motor, start)
        yield from mv(motor, end)
        yield from mv(motor, start)


.. ipython:: python
    :suppress:

    from bluesky.plan_stubs import mv
    from bluesky.preprocessors import run_decorator
    from pcdsdaq.plans import daq_decorator

    @daq_decorator(mode='on')
    @run_decorator()
    def basic_plan(motor, start, end):
        yield from mv(motor, start)
        yield from mv(motor, end)
        yield from mv(motor, start)


This plan will start the `Daq`, move ``motor`` to the ``start``, ``end``,
and back to the ``start`` positions, and then end the run.

.. ipython:: python

    RE(basic_plan(motor1, 0, 10))


If you ignore the `daq_decorator`, this is just a normal ``plan``.
This makes it simple to add the daq to a normal ``bluesky`` ``plan``.


Calib Cycles
------------
Including calib cycles in a built-in plan is as simple as including the `Daq`
as a reader or detector. The `Daq` will start and run for the configured
duration or number of events at every scan step.

The built-in ``scan`` will move ``motor1`` from ``0`` to ``10`` in ``11``
steps. Prior to the scan, we configure the ``daq`` to take ``120`` events at
each point. Since ``daq`` is included in the detectors list, it is run at every
step.

.. ipython:: python

    from bluesky.plans import scan
    daq.configure(events=120)
    RE(scan([daq], motor1, 0, 10, 11))
