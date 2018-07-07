import logging

import pytest

import pcdsdaq.ext_scripts as ext

logger = logging.getLogger(__name__)


def test_call_script():
    logger.debug('test_call_script')
    assert isinstance(ext.call_script('uname'), str)
    with pytest.raises(FileNotFoundError):
        ext.call_script('definitelynotarealscriptgeezman')


def test_hutch_name(nosim, monkeypatch):
    logger.debug('test_hutch_name')

    def fake_hutch_name(*args, **kwargs):
        return 'tst\n'

    monkeypatch.setattr(ext, 'call_script', fake_hutch_name)
    assert ext.hutch_name() == 'tst'


def test_run_number(nosim, monkeypatch):
    logger.debug('test_run_number')

    def fake_run_number(*args, **kwargs):
        return '1\n'

    monkeypatch.setattr(ext, 'call_script', fake_run_number)
    assert ext.get_run_number(hutch='tst', live=True) == 1
