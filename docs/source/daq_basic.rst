Basic Usage
===========
The `Daq` class allows a user to connect to the LCLS1 daq and control it.
For this to work, the daq must be up and allocated.

The most important method is `Daq.begin`. This will connect, configure,
and start running the daq all in one call. `Daq.stop` can be used to stop
acquiring data without ending a run. `Daq.begin` can be called again to
resume a stopped run. `Daq.end_run` will end the run.

I will step through the basic options for `Daq.begin` below. You can consult
the full `api docs <./daq_api>` for more information.

Creating a `Daq` object
-----------------------
First, I will set up the `Daq` class in simulated mode. In practice, the
`Daq` class will be set up for you in the ``hutch-python`` configuration.

.. ipython:: python

    import time
    from pcdsdaq.daq import Daq
    from pcdsdaq.sim import set_sim_mode

    set_sim_mode(True)
    daq = Daq(platform=4)  # Defined per hutch


Running Until Stop
------------------
Calling `Daq.begin` with no arguments in the default configuration will
run the daq indefinitely, until we manually stop it.

.. ipython:: python

    start = time.time()
    daq.begin()
    time.sleep(1)
    daq.stop()
    print(time.time() - start)


Running for a Fixed Number of Events
------------------------------------
Use the ``events`` argument to specify duration in number of events.
The duration of this run will depend on the current beam rate.
Optionally, we can call `Daq.wait` to pause until acquisition is complete.

.. ipython:: python

    start = time.time()
    daq.begin(events=240)  # 120Hz
    daq.wait()
    print(time.time() - start)


Runing for a Fixed Time Duration
--------------------------------
Use the ``duration`` argument to specify duration in seconds.
We can pass the ``wait`` argument to skip the `Daq.wait` call.

.. ipython:: python

    start = time.time()
    daq.begin(duration=1.5, wait=True)
    print(time.time() - start)


Recording Data
--------------
You must call `Daq.configure` to record data. This is fairly simple:

.. ipython:: python
    daq.configure(record=True)


After this call, future calls to `Daq.begin` will record data to disk.
You can undo this the same way:

.. ipython:: python
    daq.configure(record=False)


Advanced Options
----------------
- ``use_l3t=True``: This will reinterpret the ``events`` argument as
                    "the number of events that pass the level 3 trigger."
- ``controls=[motor1, motor2...]``: This will post the name of each motor and
                    the current position to the daq data stream. This is
                    handled automatically with some of the ``bluesky`` tools.
