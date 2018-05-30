Release History
###############

Next Release
============

Features
--------
- The `connect` method will provide more helpful error messages when it fails.

Deprecations
------------
- The daq no longer needs to be passed a ``platform`` argument. This argument
  will be removed in a future release, and will log a warning if you pass it.

v1.2.0 (2018-05-08)
===================

Features
--------
- Add the ``record`` option to the `begin` method. This allows a user running
  interactively to concisely activate recording for single runs.

v1.1.0 (2018-03-07)
===================

Features
--------
- Add ``daq.record`` property to schedule that the next run sould be
  configured with ``record=True``

Bugfixes
--------
- Fix bug where configured record was overridden on every configure

v1.0.0 (2018-03-02)
===================

- Initial release, transferred from `<https://github.com/pcdshub/pcdsdevices>`_
