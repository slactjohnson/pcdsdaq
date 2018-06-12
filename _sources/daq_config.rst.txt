Configuration
=============
Some manual configuration is necessary to record data or to run
special ``bluesky`` plans with daq support.

In general, there are two kinds of `Daq.configure` arguments:
those that are shared with `Daq.begin`, and those that are not.

Arguments that are shared between the two methods act as defaults.
For example, calling ``daq.configure(duration=3)`` will set the
no-arguments behavior of ``daq.begin()`` to run the daq for 3 seconds.

You can get the current configuration from `Daq.config`.
Shown here is the default config:

.. ipython:: python
    :suppress:

    from pcdsdaq.daq import Daq
    from pcdsdaq.sim import set_sim_mode

    set_sim_mode(True)
    daq = Daq()


.. ipython:: python

    daq.config


.. automethod:: pcdsdaq.daq.Daq.configure
   :noindex:
