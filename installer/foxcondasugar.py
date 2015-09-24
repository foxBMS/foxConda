"""
:since:     Wed Sep 16 11:48:44 CEST 2015
:author:    Tim Fuehner <tim.fuehner@iisb.fraunhofer.de>
$Id$
"""

import conda_api
import tarfile
import sys
import json
import subprocess

CHANNEL='www.foxbms.org --channel PATHTO\Anaconda_py3'

def getPackageInfo(pfname):
    _meta = None
    with tarfile.open(pfname) as _t:
        _f = _t.extractfile('info/index.json')
        _meta = json.loads(_f.read())
        _f.close()
    return _meta

def searchPackage(spec):
    _args = 'conda search --spec --names-only'.split(' ') + [spec]
    try:
        out = subprocess.check_output(_args)
    except Exception, e:
        print >>sys.stderr, e
        return False
    _name =  spec.split('=')[0].split(' ')[0].strip()
    out = out.split('\n')[-2].strip()
    print _name, out, spec
    if out == _name:
        return True
    return False

def searchDependencies(pkgname):
    _met = []
    _un = []
    _pkgs = getPackageInfo(pkgname)['depends']
    for p in _pkgs:
        _p = p.split(' ')
        if not searchPackage(p):
            _un += [_p]
        else:
            _met += [_p]

    return _met, _un


if __name__ == '__main__':
    print searchDependencies(sys.argv[1])



