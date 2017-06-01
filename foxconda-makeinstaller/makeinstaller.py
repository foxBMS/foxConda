"""
:since:  Fri Feb 17 11:23:41 CET 2017
:author: Tim Fuehner <tim.fuehner@iisb.fraunhofer.de>
$Id$
"""
import logging
import sys
import os
import subprocess
import shutil
import argparse
import platform
import urllib

class MakeInstaller(object):

    def __init__(self):
        self.platform = platform.system().lower()
        pass

    def condaExecute(self, command):
        logging.info(command)
        if self.platform.startswith('win'):
            p = subprocess.Popen('cmd.exe /k', stdin=subprocess.PIPE, stdout=None, stderr=None, shell=True,)
        else:
            p = subprocess.Popen('sh', stdin=subprocess.PIPE, stdout=None, stderr=None, shell=True,)
        p.stdin.write(command)
        _out, _err = p.communicate()

    def make(self):
        _cmd =r'''fcgetrepository file:///{}
fcmakepayload repodata.json
fcmakeinstaller installer.yaml
'''.format(os.path.join(sys.prefix, 'conda-bld'))

        self.condaExecute(_cmd)

    def clean(self):
        for f in ['repodata.json', 'payload.tar', '_install.spec']:
            try:
                os.remove(f)
            except Exception, e:
                logging.error(e)

        for d in ['build', 'dist', 'meta-recipe']:
            try:
                shutil.rmtree(d)
            except Exception, e:
                logging.error(e)

def main():
    parser = argparse.ArgumentParser(description='foxConda installer make script')
    parser.add_argument('--verbosity', '-v', action='count', default=0, help="increase output verbosity")
    parser.add_argument('target', nargs='?', default = 'all', metavar='TARGET',
            choices=['all', 'clean'], help='target (all|clean)')

    args = parser.parse_args()

    if args.verbosity == 1:
        logging.basicConfig(level = logging.INFO)
    elif args.verbosity > 1:
        logging.basicConfig(level = logging.DEBUG)
    else:
        logging.basicConfig(level = logging.WARNING)

    if args.target == 'all': 
        MakeInstaller().make()
    else:
        MakeInstaller().clean()

if __name__ == '__main__':
    main()
