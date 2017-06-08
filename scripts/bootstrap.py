"""
:since:     Wed Feb 15 11:18:16 CET 2017
:author:    Tim Fuehner <tim.fuehner@iisb.fraunhofer.de>
$Id$
"""

import argparse
import logging
import platform
import sys
import urllib2
import ssl
import tempfile
import subprocess
import os
import shutil
import yaml
import glob

#conda list --json --show-channel-urls


class BootstrapEnv(object):

    def __init__(self, directory, packagefname = 'packages.yaml',
            recipesdir=None, force=False):
        self.packagefname = packagefname
        self.force = force
        self.directory = directory
        self.recipesdir = recipesdir
        self.mcURL = 'https://repo.continuum.io/miniconda/'
        self.platform = platform.system().lower()
        self.mc = {
                'linux': 'Miniconda2-latest-Linux-x86_64.sh',
                'darwin': 'Miniconda2-latest-MacOSX-x86_64.sh',
                'windows': 'Miniconda2-latest-Windows-x86_64.exe',
                }


    def installMC(self):
        if os.path.exists(self.directory):
            if self.force:
                logging.info('removing {}'.format(self.directory))
                shutil.rmtree(self.directory)
            else:
                raise RuntimeError('directory {} exists'.format(self.directory))

        tmpd = tempfile.mkdtemp()
        _file = os.path.join(tmpd, self.mc[self.platform])
        logging.info('getting installer {}'.format(self.mcURL + self.mc[self.platform]))

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        response = urllib2.urlopen(self.mcURL + self.mc[self.platform], context=ctx)
        html = response.read()
        with open(_file, 'wb') as f:
            f.write(html)
        # doesn't work on Windows
        if self.platform.startswith('win'):
            _command = [_file, '/InstallationType=JustMe', '/RegisterPython=0', '/AddToPath=0', '/S', '/D=' + self.directory]

        else:
            _command = ['/bin/sh', _file, '-b', '-p', self.directory]

        logging.info('Executing Installer')
        logging.debug(" ".join(_command))
        status = subprocess.call(" ".join(_command), shell=True) 
        shutil.rmtree(tmpd)
        logging.info('miniconda deployed in %s' % self.directory)


    def condaExecute(self, command):
        logging.info(command)
        # TODO windows
        _command = 'sh'
        if self.platform.startswith('win'):
            _command = 'cmd.exe'
        p = subprocess.Popen(_command, stdin=subprocess.PIPE,
                stdout=None, stderr=None, shell=True,)
        p.stdin.write(command)
        _out, _err = p.communicate()
        if 0 and self.platform.startswith('win'):
            p.stdin.flush()


    def installPackage(self, package, fromCondaBld = False):
        if fromCondaBld:
            channel = ' -c ' + os.path.join(self.directory, 'conda-bld')
            force = ' -f'
        else:
            channel = ''
            if package in self.packages['channels']:
                channel = ' -c ' + self.packages['channels'][package]
            force = ''
        if self.platform.startswith('win'):
            _cmd = '''\
{}\\scripts\\activate root
conda install -y{}{} {}
'''.format(self.directory, force, channel, package)
            self.condaExecute(_cmd)
        else:
            _cmd = '''\
. {}/bin/activate root
conda install -y{}{} {}
'''.format(self.directory, force, channel, package)
            self.condaExecute(_cmd)

    def buildPackage(self, package):
        if self.platform.startswith('win'):
            self.condaExecute('''
set PATH={}\\Scripts:%PATH%
{}\\scripts\\activate root
conda build {}
'''.format(self.directory, self.directory, os.path.join(self.recipesdir, package)))
        else:
            self.condaExecute('''
export PATH={}/bin:$PATH
. {}/bin/activate root
conda build {}
'''.format(self.directory, self.directory, os.path.join(self.recipesdir, package)))

    def installPackages(self, packages):
        if packages[0].lower() == 'none': return
        _pp = self.packages['installpackages']
        if packages[0].lower() != 'all':
            _pp = [x for x in _pp if x in packages]
        _defaults =[x for x in _pp if not x in self.packages['channels']]
        _channeled =[x for x in _pp if x in self.packages['channels']]
        if len(_defaults) > 0:
            _packages = ' '.join(_defaults)
            if self.platform.startswith('win'):
                _cmd = '''
set PATH={}\\Scripts:%PATH%
{}\\scripts\\activate root
conda info
conda install {}
    '''.format(self.directory, self.directory, _packages)
            else:
                _cmd = '''
export PATH={}/bin:$PATH
. {}/bin/activate root
which conda
conda info
conda install {}
    '''.format(self.directory, self.directory, _packages)
            self.condaExecute(_cmd)

        for p in _channeled:
            self.installPackage(p)


    def buildPackages(self, packages):
        if packages[0].lower() == 'none': return
        _pp = self.packages['buildpackages']
        if packages[0].lower() != 'all':
            _pp = [x for x in _pp if x in packages]
        for p in _pp:
            self.buildPackage(p)
            self.installPackage(p, True)

    def readPackageList(self):
        with open(self.packagefname) as f:
            self.packages = yaml.load(f.read())
        for i,p in enumerate(self.packages['installpackages']):
            if type(p) == dict:
                self.packages['installpackages'][i] = p.keys()[0]


    def upload(self):
        # FIXME Windows
        _cmd = '''
. {}/bin/activate root
python {} -f
'''.format(self.directory, os.path.join(os.path.dirname(__file__), 'upload.py'))
        self.condaExecute(_cmd)





def main():


    parser = argparse.ArgumentParser(description='foxConda bootstrapper')
    parser.add_argument('--verbosity', '-v', action='count', default=0, help="increase output verbosity")
    parser.add_argument('--packages', '-p', default='packages.yaml', help="yaml filename containing packages")
    parser.add_argument('--recipesdir', '-d',
            default=os.path.abspath('recipes'), help="location of recipes directory")
    parser.add_argument('--reuse', '-r', action='store_true', help="use existing bootstrap directory")
    parser.add_argument('--force', '-f', action='store_true', help="force removal of current bootstrap directory")
    parser.add_argument('--install', '-i', default='all', help="install the following packages all|none|<NAME>")
    parser.add_argument('--build', '-b', default='all', help="build the following packages all|none|<NAME>")
    parser.add_argument('--upload', '-u', action='store_true', help="upload to repository")
    parser.add_argument('installdir', metavar = 'INSTALLDIR', help='directory where to install the foxconda bootstrap file')

    args = parser.parse_args()

    if args.verbosity == 1:
        logging.basicConfig(level = logging.INFO)
    elif args.verbosity > 1:
        logging.basicConfig(level = logging.DEBUG)
    else:
        logging.basicConfig(level = logging.WARNING)

    _installdir = os.path.abspath(args.installdir)

    bcenv = BootstrapEnv(_installdir, args.packages, args.recipesdir,
            force=args.force)
    bcenv.readPackageList()
    if not args.reuse:
        try:
            bcenv.installMC()
        except Exception, e:
            logging.error(e)
            sys.exit(-1)
    bcenv.installPackages(args.install.split(','))
    bcenv.buildPackages(args.build.split(','))
    if args.upload:
        bcenv.upload()


if __name__ == '__main__':
    main()
