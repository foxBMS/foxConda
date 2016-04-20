# -*- mode: python -*-
import os
import glob
from conda import config

ROOT = os.path.abspath('..')

datafiles =  [('condapackages.tar', os.path.join(ROOT, 'data', 'condapackages-%s.tar' % config.subdir), 'DATA')]
datafiles += [('LICENSE-ANACONDA.txt', os.path.join(ROOT, 'data', 'LICENSE-ANACONDA.txt'), 'DATA')]
datafiles += [('license-foxbms.txt', os.path.join(ROOT, 'data', 'license-foxbms.txt'), 'DATA')]

print datafiles

a = Analysis([os.path.join(ROOT, 'install.py')],
             pathex=[ROOT],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas + datafiles,
          name='foxcondainstall',
          debug=False,
          strip=None,
          upx=True,
          console=True )
