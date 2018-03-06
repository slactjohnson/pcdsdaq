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
and turn it off at the end of the plan. This is done using the default mode,
``on``, which we'll configure explicitly in the `daq_wrapper`.

.. code-block:: python

    from bluesky.plan_stubs import mv
    from bluesky.preprocessors import run_decorator
    from pcdsdaq.plans import daq_decorator

    @daq_decorator(mode='on')
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


Calib Cycle Per Step
--------------------
Including calib cycles in a built-in plan with a ``per_step`` hook
is also simple using `calib_at_step`. Take care to make sure the `Daq` is
configured with ``mode='manual'``.

.. code-block:: python

    from bluesky.plans import scan
    from pcdsdaq.plans import calib_at_step

    def daq_scan(dets, motor, start, end, steps, events_per_point, record=False):
        @daq_decorator(mode='manual', record=record)
        def inner_daq_scan():
            yield from scan(dets, motor, start, end, steps,
                            per_step=calib_at_step(events=events_per_point)
        return (yield from inner_daq_scan())


.. ipython:: python
    :suppress:

    from bluesky.plans import scan
    from pcdsdaq.plans import calib_at_step

    def daq_scan(dets, motor, start, end, steps, events_per_point, record=False):
        @daq_decorator(mode='manual', record=record)
        def inner_daq_scan():
            yield from scan(dets, motor, start, end, steps,
                            per_step=calib_at_step(events=events_per_point)
        return (yield from inner_daq_scan())


This plan will move ``motor`` from ``start`` to ``end`` in ``steps``
evenly-spaced steps, checking readings from ``dets`` at each point
and running a `calib_cycle` for ``events_per_point`` events.

.. ipython:: python

    RE(daq_scan([det1], motor1, 0, 10, 11, 120))


Manual Calib Cycle
------------------
You may also call `calib_cycle` directly:

.. code-block:: python

    from bluesky.plan_stubs import sleep
    from pcdsdaq.plans import calib_cycle

    def daq_count(num, sleep_time, duration_per_point, record=False):
        @daq_decorator(mode='manual', record=record)
        @run_decorator()
        def inner_daq_count():
            for i in range(num):
                yield from calib_cycle(duration=duration_per_point)
                yield from sleep(sleep_time)
        return (yield from inner_daq_count())


.. ipython:: python
    :suppress:

    from bluesky.plan_stubs import sleep
    from pcdsdaq.plans import calib_cycle

    def daq_count(num, sleep_time, duration_per_point, record=False):
        @daq_decorator(mode='manual', record=record)
        @run_decorator()
        def inner_daq_count():
            for i in range(num):
                yield from calib_cycle(duration=duration_per_point)
                yield from sleep(sleep_time)
        return (yield from inner_daq_count())


This plan will run `calib_cycle` ``num`` times for ``duration_per_point``
seconds each, waiting ``sleep_time`` seconds between cycles.

.. ipython:: python

    RE(daq_count(5, 2, 3, record=True))


Auto Mode
---------
In addition to ``on`` and ``manual`` modes, an ``auto`` mode exists. This will
run the daq for the duration of time that a normal ``bluesky`` plan is reading
data. This is between ``create`` and ``save`` messages.
