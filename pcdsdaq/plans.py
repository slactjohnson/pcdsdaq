"""
This module defines utilities for incorporating the daq into a bluesky plan.
"""
from bluesky.plan_stubs import configure, kickoff, complete, one_nd_step
from bluesky.preprocessors import fly_during_wrapper
from bluesky.utils import make_decorator

from .daq import get_daq


def daq_wrapper(plan, **config):
    """
    Run a plan with the `Daq`. This must be applied outside the
    ``run_wrapper``. All configuration must be done either by supplying
    config kwargs to this wrapper or by calling `Daq.configure` prior to
    entering the `daq_wrapper`.

    The `daq_decorator` is the same as the `daq_wrapper`, but it is meant to be
    used as a function decorator.

    Parameters
    ----------
    plan: ``plan``
        The ``plan`` to use the daq in

    config: kwargs
        See `Daq.configure`. These keyword arguments will be passed directly to
        the daq's configuration routine.
    """
    try:
        daq = get_daq()
        if config:
            yield from configure(daq, **config)
        daq._RE.msg_hook = daq._interpret_message
        yield from fly_during_wrapper(plan, flyers=[daq])
        daq._RE.msg_hook = None
    except Exception:
        daq._RE.msg_hook = None
        raise


daq_decorator = make_decorator(daq_wrapper)


def calib_cycle(events=None, duration=None, use_l3t=None, controls=None):
    """
    Plan to put the daq through a single calib cycle. This will start the daq
    with the configured parameters and wait until completion. This will raise
    an exception if the daq is configured to run forever or if we aren't using
    the `daq_wrapper`.

    All omitted arguments will fall back to the configured value.

    Parameters
    ----------
    events: ``int``, optional
        Number events to take in the daq.

    duration: ``int``, optional
        Time to run the daq in seconds, if ``events`` was not provided.

    use_l3t: ``bool``, optional
        If ``True``, we'll run with the level 3 trigger. This means that, if we
        specified a number of events, we will wait for that many "good"
        events as determined by the daq.

    controls: ``dict{name: device}`` or ``list[device...]``, optional
        If provided, values from these will make it into the DAQ data
        stream as variables. We will check ``device.position`` and
        ``device.value`` for quantities to use and we will update these values
        each time begin is called. To provide a list, all devices must
        have a ``name`` attribute.
    """
    def inner_calib_cycle():
        daq = get_daq()
        if daq._RE.state == 'running':
            if not daq._is_bluesky:
                raise RuntimeError('Daq is not attached to the RunEngine! '
                                   'We need to use a daq_wrapper on our '
                                   'plan to run with the daq!')
            if not any((events, duration, daq.config['events'],
                        daq.config['duration'])):
                raise RuntimeError('Daq is configured to run forever, cannot '
                                   'calib cycle. Please call daq.configure or '
                                   'calib cycle with a nonzero events or '
                                   'duration argument.')
        yield from kickoff(daq, wait=True, events=events, duration=duration,
                           use_l3t=use_l3t, controls=controls)
        yield from complete(daq, wait=True)

    return (yield from inner_calib_cycle())


def calib_at_step(events=None, duration=None, use_l3t=None, controls=None):
    """
    Create a ``per_step`` hook suitable for built-in ``bluesky`` plans.

    This hook will move the motors, read the detectors, and
    put the daq through one calib cycle at each step. Arguments passed to
    this function will be passed through to `calib_cycle` at each step.

    The controls argument will default to the detectors and the motors in the
    plan, because this information is available to the ``per_step`` hook. All
    other parameters will act as in `calib_cycle`.

    Returns
    -------
    inner_calib_at_step: plan
        Plan suitable for use as a per_step hook
    """
    def inner_calib_at_step(detectors, step, pos_cache):
        if controls is None:
            controls_arg = detectors + list(step.keys())
        else:
            controls_arg = controls
        yield from one_nd_step(detectors, step, pos_cache)
        yield from calib_cycle(events=events, duration=duration,
                               use_l3t=use_l3t, controls=controls_arg)
    return inner_calib_at_step
