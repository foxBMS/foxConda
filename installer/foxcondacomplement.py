"""
:since:     Mon Aug 03 17:39:58 CEST 2015
:author:    Tim Fuehner <tim.fuehner@iisb.fraunhofer.de>
$Id$
"""

import sys
import os
import glob
import subprocess

with open('include.txt') as _f:
    _p = [x.strip() for x in _f.readlines() if x.strip != '' and not x.strip().startswith('conda')]


subprocess.call(['conda', 'install', '-y'] + _p)


