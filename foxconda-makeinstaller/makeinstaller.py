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
import yaml

class MakeInstaller(object):

    def __init__(self, configfile = 'installer.yaml'):
        '''
        :param configfile:  default 'installer.yaml'. Change this if it has
                            a different name
        .. note::

           FIXME: make it an option

        '''
        self.platform = platform.system().lower()
        if self.platform == 'darwin':
            self.platform = 'macos'
        with open(configfile, 'r') as f:
            y = yaml.load(f.read())
        self.name = y['name']
        self.version = y['version']


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

    def rename(self):

        # rename installer to reflect version and platform, assign build
        # number if an installer with the same name is already present
        _src = os.path.join('dist', self.name)
        _trg = os.path.join('dist', '-'.join([self.name, self.platform, self.version]))
        _ext = ''
        if self.platform.startswith('win'):
            _ext = '.exe'
            _src += '.exe'
        _t = _trg + _ext
        i = 0
        while os.path.exists(_t):
            i += 1
            _t = '%s_%.3d%s' % (_trg, i, _ext) 
        _trg = _t
        shutil.move(_src, _trg)

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
            choices=['all', 'rename', 'clean'], help='target (all|rename|clean)')

    args = parser.parse_args()

    if args.verbosity == 1:
        logging.basicConfig(level = logging.INFO)
    elif args.verbosity > 1:
        logging.basicConfig(level = logging.DEBUG)
    else:
        logging.basicConfig(level = logging.WARNING)


    if args.target == 'all': 
        mk = MakeInstaller()
        mk.make()
        mk.rename()
    elif args.target == 'rename': 
        mk = MakeInstaller()
        mk.rename()
    elif args.target == 'clean':
        mk = MakeInstaller()
        mk.clean()

if __name__ == '__main__':
    main()
