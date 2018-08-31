Basic Usage
===========
The `AmiDet` class can be used to read the mean and rms of an ami variable
over time. This can be useful for keeping track of DAQ scans in the python
layer.

This module should be set up automatically in a hutch python session, but if
you're running this on your own then you'll need to call `set_ami_proxy` and
`set_l3t_file` before the class will work.

Creating an AmiDet object
-------------------------
This code will set up an `AmiDet` object in simulated mode. Replace
``'AMI-NAME'`` with the name used in AMI to reference the data, and replace
``'ami_det'`` with the desired table label in the ``bluesky`` scans.

.. code-block:: python

    from pcdsdaq.ami import AmiDet
    from pcdsdaq.sim import set_sim_mode

    set_sim_mode(True)
    det = AmiDet('AMI-NAME', name='ami_det')


.. ipython:: python
    :suppress:

    import time
    from pcdsdaq.ami import AmiDet
    from pcdsdaq.sim import set_sim_mode

    set_sim_mode(True)
    det = AmiDet('AMI-NAME', name='ami_det')


In a Scan
---------
These `AmiDet` objects should be added to the ``dets`` list of a ``bluesky``
scan. If used as configured above, they will collect data at each scan step
while the daq is running. Below is an example scan, see the `plans_basic` page
for general information about daq scans.

.. ipython:: python
    :suppress:

    from bluesky import RunEngine
    from pcdsdaq.daq import Daq
    
    RE = RunEngine({})
    daq = Daq(RE=RE)


.. ipython:: python

    from bluesky.plans import count
    # Configure the daq for 120 events at each point
    daq.configure(events=120)
    # Run the daq and read det 10 times
    RE(count([daq, det], 10))
   

Interactively
-------------
You can also use `AmiDet` interactively, perhaps in a second session, to snoop
on AMI information. Use the ``trigger`` method to start or restart data
acquisition and the ``get`` method to check the accumulated statistics.


Advanced Options
----------------
- Use the ``filter_string`` kwarg or set ``det.filter_string`` to filter the
  incoming data for the `AmiDet`.
- Use the ``min_duration`` kwarg or set ``det.min_duration`` to a positive
  number to specify a minimum time spent measuring data at each point. This is
  not needed if you are running pydaq and pyami in the same scan, but it may be
  useful if you are free-running the daq and need to control acquisition times
  in your scan.
