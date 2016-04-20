"""
:since:     Mon Aug 03 13:53:03 CEST 2015
:author:    Tim Fuehner <tim.fuehner@iisb.fraunhofer.de>

Using miniconda. Heavily inspired by Miniconda installation routine.
$Id$
"""

#conda config --add channels 'ftp://pappel.iisb.fraunhofer.de:21/pub/dldeploy/conda/channel'

import argparse
import os
import sys
import shutil
import tarfile
import re
import glob
import subprocess


import shlex
import struct
import platform
 
 
def get_terminal_size():
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        print "default"
        tuple_xy = (80, 25)      # default value
    return tuple_xy
 
 
def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass
 

def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass
 
 
def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])





class FoxInstaller(object):

    CHANNELS = ['http://www.foxbms.org/foxconda/channel']
    LICENSES = ['license-foxbms.txt', 'LICENSE-ANACONDA.txt']

    def __init__(self):
        self.batch = False
        self.thispath = getattr(sys, '_MEIPASS', os.getcwd())
        #self.license = os.path.join(self.thispath, 'LICENSE-ANACONDA.txt')
        self.prefix = None
        #self.pkgsdir = os.path.join(self.prefix, 'pkgs')

    def doArgs(self):
        parser = argparse.ArgumentParser(description='Installer commandline arguments')
        parser.add_argument('-p', '--prefix', 
                type=unicode,
                default=None,
                help='installation prefix')
        parser.add_argument('-b', '--batch', action='store_true')
        args = parser.parse_args()
        self.args = args
        self.prefix = args.prefix
        self.batch = args.batch
        self.conda = None
        self.python = None
        self.thispython = sys.executable

    def getChoices(self, choices = {'y*': 'yes', 'n*': 'no'}, 
            prompt='yes/no? ', invalid='Invalid input. Type yes or no', case=False):

        for k,v in choices.iteritems():
            if k.endswith('*'):
                _s = len(k) - 1
                for i in range(_s, len(v)):
                    choices[k + v[_s:i + 1]] = v
                del choices[k]

        while 1:
            ans = raw_input(prompt)
            if not case:
                ans = ans.lower()
            try:
                return choices[ans]
            except:
                print invalid

    
    def queryPrefixandMkdir(self):
        """
        :postcondition: 
            - :attr:`prefix` contains the absolute user installation path
            - :attr:`pkgsdir` contaisn the absolute ``pkgs`` dir
        """
        _default = os.path.join(os.path.expanduser('~'), 'foxconda')
        if not self.args.prefix is None:
            self.prefix = os.path.expanduser(self.args.prefix)
            while 1:
                if os.path.exists(self.prefix):
                    print "Directory %s exists. Please manually remove it or choose another name." % self.prefix
                    ans = self.getChoices(choices={'r*': 'retry', 'n*': 'new', 'a*': 'abort'}, 
                        prompt='Press r: retry, n: new directory or a: abort', 
                        invalid='invalid input. Press r: retry, n: new directory or a: abort')
                    if ans == 'abort':
                        sys.exit(0)
                    else:
                        self.prefix = None
                        break


        if self.prefix is None:
            while 1:
                ans = raw_input('Into what directory do you want to install foxConda [%s]?\n' % _default + \
                        'Installation Directory: ')
                if ans.strip() == '': ans = _default
                if os.path.exists(ans):
                    print "Directory %s exists. Choose a different location." % ans
                else:
                    try:
                        os.makedirs(ans)
                        os.makedirs(os.path.join(ans, 'envs'))
                        self.prefix = ans
                        self.pkgsdir = os.path.join(self.prefix, 'pkgs')
                        break
                    except Exception, e:
                        print "Cannot create directory. Choose a different location."
 
    def showLicense(self):
        x,y = get_terminal_size()
        print(chr(27) + "[2J")

        _lines = []
        for l in self.LICENSES:
            with open(os.path.join(self.thispath, l), 'r') as _f:
                _lines += _f.read().split('\n') + ['\n']

        i = 0
        while 1:
            ii = min(i + y - 3, len(_lines) - 1)
            print(chr(27) + "[2J")
            print '\n'.join(_lines[i:ii])
            if ii >= (len(_lines) - 1):
                break
            raw_input('Press ENTER to continue')
            i += y - 6

        while 1:
            inp = raw_input('Do you accept the terms of both the Anaconda\n' + 'and the foxBMS license (yes/no)? ').lower()
            if not inp in ['y', 'yes', 'n', 'no']:
                print 'Invalid input. Type yes or no.'
            elif inp in ['n', 'no']:
                print '\nLicense not accepted. Aborting.'
                sys.exit(0)
            else:
                break

    def getDists(self):
        return ['.'.join(x.split('.')[:-2]) for x in os.listdir(os.path.join(self.prefix, 'pkgs'))]

    def install(self):


        try:
            os.makedirs(os.path.join(os.path.expanduser('~'), '.continuum'))
        except Exception, e:
            pass

        for l in self.LICENSES:
            shutil.copy(os.path.join(self.thispath, l), self.prefix)

        thisdir = os.path.abspath('.')
        os.chdir(self.prefix)
        with tarfile.open(os.path.join(self.thispath, 'condapackages.tar')) as _f:
            _f.extractall()
        os.chdir(thisdir)

        for d in self.getDists():
            if not re.match('conda-\d', d) is None:
                self.conda = d
            elif not re.match('python-\d', d) is None:
                self.python = d
            self.extract(d)

        _pythonpath = os.path.join(self.pkgsdir, self.python, 'bin', 'python')
        #$PREFIX/pkgs/conda-3.9.1-py27_0/lib/python2.7/site-packages/conda/install.py

        _condapath = os.path.join(self.pkgsdir, self.conda, 'lib', 'python2.7', 'site-packages', 'conda')
        _install = os.path.join(_condapath, 'install.py')
        #_args = sys.argv
        #sys.argv = ['conda', '--prefix=%s' % self.prefix, '--pkgs-dir=%s' % self.pkgsdir, '--link-all']
        print 'Linking packages'
        _args = [_pythonpath, _install, '--prefix=%s' % self.prefix, '--pkgs-dir=%s' % self.pkgsdir, '--link-all']
        out = subprocess.check_output(_args)

        print 'Installing dependencies'

        _condapath = os.path.join(self.prefix, 'bin', 'conda')
        _deps = glob.glob(os.path.join(self.prefix, 'foxconda-deps-*.tar.bz2'))
        _args = [_condapath, 'install', '-y'] 
        for c in self.CHANNELS:
            _args += ['--channel', c]
        _args += [_deps[0]]
        print ' '.join(_args)
        #out = subprocess.check_output(_args)
        subprocess.call(' '.join(_args), shell=True)
        #sys.argv = ['conda', '--prefix=%s' % self.prefix, '--pkgs-dir=%s' % self.pkgsdir, _deps[0]]


    def extract(self,  dist):
        """
        Extract a package, i.e. make a package available for linkage.  We assume
        that the compressed packages is located in the packages directory.

        adopted from install.py of conda by Continuum Analytics
        """

        print("installing %s ..." % dist)

        path = os.path.join(self.pkgsdir, dist)
        t = tarfile.open(path + '.tar.bz2')
        t.extractall(path=path)
        t.close()

        if sys.platform.startswith('linux') and os.getuid() == 0:
            # When extracting as root, tarfile will by restore ownership
            # of extracted files.  However, we want root to be the owner
            # (our implementation of --no-same-owner).

            for root, dirs, files in os.walk(path):
                for fn in files:
                    os.lchown(os.path.join(root, fn), 0, 0)


def main():
    fi = FoxInstaller()
    fi.doArgs()
    fi.showLicense()
    fi.queryPrefixandMkdir()
    fi.install()


if __name__ == '__main__':
    main()

