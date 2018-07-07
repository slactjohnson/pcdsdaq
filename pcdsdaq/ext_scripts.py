import logging
import subprocess


logger = logging.getLogger(__name__)
SCRIPTS = '/reg/g/pcds/engineering_tools/{}/scripts/{}'


def call_script(args):
    logger.debug('Calling external script %s', args)
    try:
        return subprocess.check_output(args, universal_newlines=True)
    except Exception:
        logger.debug('Exception raised from %s', args, exc_info=True)
        raise


def hutch_name():
    script = SCRIPTS.format('latest', 'get_hutch_name')
    name = call_script(script)
    return name.lower().strip(' \n')


def get_run_number(hutch=None, live=False):
    latest = hutch or 'latest'
    script = SCRIPTS.format(latest, 'get_lastRun')
    args = [script]
    if hutch is not None:
        args += ['-i', hutch]
    if live:
        args += ['-l']
    run_number = call_script(args)
    return int(run_number)
