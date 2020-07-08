import logging
import re
import socket
import subprocess


logger = logging.getLogger(__name__)
CNF = '/reg/g/pcds/dist/pds/{0}/scripts/{0}.cnf'
SCRIPTS = '/reg/g/pcds/engineering_tools/{}/scripts/{}'
TOOLS = '/reg/g/pcds/dist/pds/tools/{}/{}'


def call_script(args, timeout=None, ignore_return_code=False):
    logger.debug('Calling external script %s with timeout=%s,'
                 ' ignore_fail=%s', args, timeout, ignore_return_code)
    try:
        return subprocess.check_output(args, universal_newlines=True,
                                       timeout=timeout)
    except subprocess.CalledProcessError as exc:
        if ignore_return_code:
            return exc.output
        else:
            logger.debug('CalledProcessError from %s', args, exc_info=True)
            raise
    except Exception:
        logger.debug('Exception raised from %s', args, exc_info=True)
        raise


def hutch_name(timeout=5):
    script = SCRIPTS.format('latest', 'get_hutch_name')
    name = call_script(script, timeout=timeout)
    return name.lower().strip(' \n')


def get_run_number(hutch=None, live=False, timeout=5):
    latest = hutch or 'latest'
    script = SCRIPTS.format(latest, 'get_lastRun')
    args = [script]
    if hutch is not None:
        args += ['-i', hutch]
    if live:
        args += ['-l']
    run_number = call_script(args, timeout=timeout)
    return int(run_number)


def get_ami_proxy(hutch, timeout=2):
    # This is mostly copied from old hutch python verbatim
    # I don't have useful explanations for what these regular expressions
    # are used for
    domain_re = re.compile('.pcdsn$')
    ip_re = re.compile(r'ami_proxy.*-s\s+(?P<ip>\d+\.\d+\.\d+\.\d+)')
    hutch = hutch.lower()
    cnf = CNF.format(hutch)
    procmgr = TOOLS.format('procmgr', 'procmgr')
    output = call_script([procmgr, 'status', cnf, 'ami_proxy'],
                         timeout=timeout,
                         ignore_return_code=True)
    for line in output.split('\n'):
        ip_match = ip_re.match(line)
        if ip_match:
            host, _, _ = socket.gethostbyaddr(ip_match.group('ip'))
            return domain_re.sub('', host)
