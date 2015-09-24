::make configure
::configure --prefix=%PREFIX%
::make all
::make install

::cd %PREFIX%
::del lib lib64
::del share/man
::strip bin\* || echo
::strip libexec\git-core\* || echo


PortableGit-2.5.0-64-bit.7z.exe
copy bld.bat %PREFIX%
cd PortableGit
xcopy * %PREFIX% /E /C
