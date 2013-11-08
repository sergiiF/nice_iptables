#!/usr/bin/env python
__author__ = 'sergii'

import argparse
import functools
import os


VENV_DIR = '.venv'
PKG_NAME = 'test_project'


def run_cmd(prefix, cmd):
    if prefix:
        cmd = ' && '.join([prefix, cmd])
    ret_code = os.system(cmd)
    if ret_code:
        raise RuntimeError('cmd: %(cmd)s failed with return code %(ret_code)s'
                           % locals())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--no_pep8', action='store_true', default=False,
                        help='Do not run pep8')
    parser.add_argument('--no_ut', action='store_true', default=False,
                        help='Do not run UT')
    parser.add_argument('--no_venv', action='store_false', default=False,
                        help='Do not install venv')
    parser.add_argument('--coverage', action='store_true',
                        help='Generate coverage report')
    args = parser.parse_args()

    prefix = ''

    if not args.no_venv:
        if not os.path.exists(VENV_DIR):
            print 'Create virtual environment'
            run_cmd('', 'virtualenv %s' % VENV_DIR)
        prefix = '. %s/bin/activate' % VENV_DIR

    run_cmd = functools.partial(run_cmd, prefix)

    if not args.no_venv:
        print 'Run develop installation'
        run_cmd('python setup.py develop')

    if not args.no_pep8:
        print 'Run PEP8 check'
        run_cmd('flake8 %s' % PKG_NAME)

    if not args.no_ut:
        print 'Run unit tests',
        ut_cmd = ['nosetests']
        if args.coverage:
            ut_cmd.append('--with-coverage --cover-package=%s' % PKG_NAME)
            run_cmd('coverage erase')
        ut_cmd.append(PKG_NAME)
        run_cmd(' '.join(ut_cmd))
