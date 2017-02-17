# -*- mode: python -*-

block_cipher = None


a = Analysis(['install.py'],
             pathex=['O:\\70_Software\\2016-04-22-foxcconda-installer'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='install',
          debug=False,
          strip=False,
          upx=True,
          console=True , version='windowsexedetails.txt')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='install')
