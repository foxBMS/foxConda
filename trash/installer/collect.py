"""
:since:     Mon Aug 03 17:39:58 CEST 2015
:author:    Tim Fuehner <tim.fuehner@iisb.fraunhofer.de>
$Id$
"""

import sys
import os
import glob
from conda import config
import conda.cli
import shutil
import StringIO
import subprocess
import re
import tarfile
import json

#print(dir(sys))
#print(sys.prefix)

PACKAGE = 'condapackages-%s.tar' % config.subdir

METAPACKAGE = 'foxconda-deps'
METAVERSION = '0.1'
METABUILDNR = 0

def discover(req):
    _pkgs = []
    for p in config.pkgs_dirs:
        #_pkgs += glob.glob(os.path.join(p, req + '-[0-9]*.tar.bz2'))
        try:
            _pkgs += glob.glob(os.path.join(p, req + '*.tar.bz2'))
        except:
            _pkgs += glob.glob(os.path.join(p, req + '-[0-9]*.tar.bz2'))
    _pkgs.sort()
    return _pkgs


def main():

    with open('include.txt') as _f:
        _include = _f.read().strip().split('\n')

    try:
        out = subprocess.check_output(['conda', 'list', '--export', '-n', 'foxconda'])
    except Exception, e:
        print >>sys.stderr, e

    try:
        out += '\n' + subprocess.check_output(['conda', 'list', '--export', 'conda-env'])
    except Exception, e:
        print >>sys.stderr, e

    try:
        _cout = json.loads(subprocess.check_output(['conda', 'info', '--json']))
    except Exception, e:
        print >>sys.stderr, e

    packages = []

    for _l in out.split('\n'):
        if not _l.startswith('#') and _l.strip() != '':
            packages += [_l.split('=')[:-1]]

    packages += [['conda', _cout['conda_version']]]


    _thisdir = os.path.abspath('.')
    _t = tarfile.open(os.path.join(_thisdir, 'data', PACKAGE), 'w')
    _depends = []

    for r in packages:
        _r = '-'.join(r)
        _pkgs = discover(_r)

        if len(_pkgs) == 0:
            _args = ['conda', 'install', '-y', '--force', '='.join(r)]
            print _args
            out = subprocess.check_output(_args)
            print out
            _pkgs = discover(_r)

        if r[0] in _include:
            _location = os.path.join('pkgs', os.path.basename(_pkgs[-1]))
            print >>sys.stderr, 'adding', _location
            os.chdir(os.path.join(os.path.dirname(_pkgs[-1]), '..'))
            _t.add(_location)
        else:
            _depends += [r]
            print >>sys.stderr, 'depends', " ".join(_depends[-1])


    if len(_depends) > 0:
        _args = ['conda', 'metapackage', '--dependencies'] + \
            ['%s %s' % (x[0], x[1]) for x in _depends] + \
            ['--build-string', str(METABUILDNR), '--', METAPACKAGE, METAVERSION]
        print ' '.join(_args)
        out = subprocess.check_output(_args)
        _location = '%s-%s-%s.tar.bz2' % (METAPACKAGE, METAVERSION, METABUILDNR)
        print >>sys.stderr, 'adding', _location
        os.chdir(os.path.join(config.root_dir, 'conda-bld', config.subdir))
        _t.add(_location)
        os.remove(_location)


    os.chdir(_thisdir)
    _t.close()

if __name__ == '__main__':
    main()


