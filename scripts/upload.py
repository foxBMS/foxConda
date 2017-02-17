"""
:since:     Wed Feb 03 12:48:51 CET 2016
:author:    Tim Fuehner <tim.fuehner@iisb.fraunhofer.de>
$Id$
"""

import argparse
import paramiko
import os
import logging
from urlparse import urlparse
import glob
import yaml
import subprocess
import sys

from conda import config

DEFAULT_CHANNELS = { }

class Uploader(object):

    # FIXME host keys expected, add password auth

    def __init__(self, host = None, user = None, path = None, port = None,
            package = None, arch = None, rconda = 'conda'):
        self.host = host
        self.user = user
        self.client = None
        self.ftpclient = None
        self.path = path
        self.port = None
        self.package = package
        self.arch = arch
        self.rconda = rconda

    def __enter__(self):
        self._open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _open(self):
        logging.info('Connecting to %s@%s ' % (self.user, self.host))
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.host, username = self.user)
        self.ftpclient = self.client.open_sftp()

    def exec_command(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        logging.info(stdout.read())
        l = stderr.read()
        if l.strip() != '':
            logging.error(l)

    def index(self):
        _cmd = 'cd ' + self.path + ' ; ' + self.rconda + ' index *'
        logging.info('running ' + _cmd)
        self.exec_command(_cmd)

    def convert(self):
        _cmd = self.rconda + ' convert -v -p all ' 
        _cmd = 'cd ' + self.path + ' ; ' + _cmd + self.arch + '/' + os.path.basename(self.package)
        logging.info('running ' + _cmd)
        self.exec_command(_cmd)

    @staticmethod
    def open(host, user):
        u = CondaUploader(host, user)
        u._open()
        return u

    def close(self):
        self.ftpclient.close()
        self.client.close()

    def upload(self, lpath, rpath):
        logging.info('Uploading %s to %s' % (lpath, self.host + '/' + rpath))
        self.ftpclient.put(lpath, rpath)

    def uploadFile(self, lpath, rdir = None):
        _rpath = rdir + '/' + os.path.basename(lpath)
        self.upload(lpath, _rpath)

    def uploadPackage(self):
        _rpath = self.path + '/' + self.arch + '/' + os.path.basename(self.package)
        self.upload(self.package, _rpath)

class HostResolver(object):


    def __call__(self, remote):

        _loc = {}
        if type(remote) in [list, tuple]:
            url = urlparse(remote[0])
            _loc['user'] = os.environ['USER']
            _loc['path'] = remote[1]
        else:
            url = urlparse('sftp://' + remote)
            _loc['user'] = url.username
            _loc['path'] = url.path

        _loc['host'] = url.hostname
        _loc['port'] = url.port
        return _loc


def findNonStandardPackages():
    p = subprocess.Popen('conda list --json --show-channel-urls',
            stdout=subprocess.PIPE, stderr=None, stdin=None, shell=True)
    pkgs = yaml.load(p.stdout.read())    
    p.communicate()
    _packages = []
    for p in pkgs:
        _p = p.split('::')
        if len(_p) > 1:
            _packages += [_p[1]]
    return _packages


class PackageResolver(object):

    def __call__(self, package):

        _loc = {}
        _loc['arch'] = config.subdir
        _loc['package'] = package
        
        if os.path.isfile(package):
            _package = package.split(os.path.sep)
            if len(_package) > 1:
                _loc['arch'] = _package[-2]
        else:
            _packages = sorted(glob.glob(os.path.join(config.root_dir, 'conda-bld', config.subdir, package + '-*.tar.*')))
            if len(_packages) < 1:
                #_packages = sorted(glob.glob(os.path.join(config.root_dir, 'pkgs', package + '-*.tar.*')))
                _packages = sorted(glob.glob(os.path.join(config.root_dir, 'pkgs', package + '*.tar.*')))
            if len(_packages) < 1:
                raise RuntimeError('no such package found %s' % package)
            _loc['package'] = _packages[-1]
        _loc['package'] = os.path.abspath(_loc['package'])
        return _loc


def main():

    logging.basicConfig(level = logging.INFO)

    parser = argparse.ArgumentParser(description='conda uploader')

    parser.add_argument('-r', '--remote', default=None,
    help='''\
specify a server path location to upload to either by a [USER@]HOST/PATH
string or a name from %s''' % str(DEFAULT_CHANNELS.keys()))  
    parser.add_argument('-c', '--conda', default=None, help='remote conda path')
    parser.add_argument('-t', '--convert', action='store_true',
            default=False, help='assume platform independent packages. Try to convert')
    parser.add_argument('-f', '--find', action='store_true', help='find all packages not coming from standard channels')
    parser.add_argument('package', nargs='*', metavar='PACKAGEFILE', help='package file')

    args = parser.parse_args()
    
    try:
        with open(os.path.expanduser('~/.condarc')) as f:
            _entries = yaml.load(f.read())    
    except:
        _entries = {}

    if args.remote is None:
        _remote = _entries['condasdk']['url'], _entries['condasdk']['lpath']
    else:
        _remote = DEFAULT_CHANNELS.get(args.remote, args.remote)
    h = HostResolver()(_remote)

    if args.conda is None:
        _conda = _entries['condasdk']['remoteconda']
    else:
        _conda = args.conda

    _packages = args.package
    if args.find:
        _packages += findNonStandardPackages()

    h['rconda'] = _conda
    with Uploader(**h) as ul:
        for p in _packages:
            kwargs = PackageResolver()(p)
            print kwargs
            #ul.arch = kwargs['arch']
            #ul.package = kwargs['package']
            #ul.uploadPackage()
            #if args.convert:
            #    ul.convert()
        #ul.index()


if __name__ == '__main__':
    main()


