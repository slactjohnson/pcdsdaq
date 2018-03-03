Configuration
=============
Some manual configuration is necessary to record data or to run
special ``bluesky`` plans with daq support.

In general, there are two kinds of ``Daq.configure`` arguments:
those that are shared with `Daq.begin`, and those that are not.

Arguments that are shared between the two methods act as defaults.
For example, calling ``daq.configure(duration=3)`` will set the
no-arguments behavior of ``daq.begin()`` to run the daq for 3 seconds.

The additional arguments are parameters that can only be changed
through the ``Daq.configure`` method.  ``record`` is a parameter that
tells the daq whether or not to save to disk, and ``mode`` is a
parameter that sets up the ``bluesky`` behavior. See
`basic usage <./daq_basic>` and
`using the daq with bluesky <./plans_basic>`.

.. automethod:: pcdsdaq.daq.Daq.configure
   :noindex:
