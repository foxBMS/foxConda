========
foxConda
========

:author:  Tim Fühner <tim.fuehner@iisb.fraunhofer.de>
:version: 0.1
:date:    2015-09-18 

Installer Creation
==================

Get Miniconda from http://pappel.iisb.fraunhofer.de/foxbms/conda/miniconda/
for your platform



Windows 7 64
------------

* Run the Miniconda executable

As installation path, use:
    ``C:\Users\fuehner\AppData\Local\Continuum\Miniconda``
MINICONDAROOT

* Open a command shell (``cmd``) and connect the BMS deployment directory
  as drive X::

      net use X: \\netapp02\deployment\bms-deployment 

* change to that drive::

    X:

* change to foxconda::

    cd foxconda\installer
    

* set the proxies::

    set http_proxy=http://http-proxy.iisb.fraunhofer.de:81
    set https_proxy=http://http-proxy.iisb.fraunhofer.de:81
    set ftp_proxy=http://http-proxy.iisb.fraunhofer.de:81

* Install *conda-build*. Make sure it's version **1.11.0**::

    MINICONDAROOT\Scripts\conda install "conda-build =1.11.0"

* Create a new environment called *“foxConda”*::

    MINICONDAROOT\Scripts\conda create -n foxconda sphinx

  Confirm (y). The environment will contain the package ``sphinx`` and all of its
  dependencies.

* Change to the newly created environment::

    activate foxconda

* Install *matplotlib* into this environment::

    MINICONDAROOT\Scripts\conda install matplotlib

* Install *scipy* (also into this environment)::

    MINICONDAROOT\Scripts\conda install scipy

* Complement the installation by running::

    MINICONDAROOT\python foxcondacomplement.py


Build extra packages
--------------------

* cmake
* doxygen
* breathe
* gcc-arm
* git

* Change into the ``recipes`` subdirectory::

    cd ..\recipes

* run::
    
    MINICONDAROOT\Scripts\conda build cmake
    MINICONDAROOT\Scripts\conda install MINICONDAROOT\conda-bld\win-64\cmake-3.3.0-0.tar.bz2
    MINICONDAROOT\Scripts\conda build doxygen
    MINICONDAROOT\Scripts\conda install MINICONDAROOT\conda-bld\win-64\doxygen-1.8.10-1.tar.bz2
    MINICONDAROOT\Scripts\conda build breathe
    MINICONDAROOT\Scripts\conda install MINICONDAROOT\conda-bld\win-64\breathe-4.0.0-py27_0.tar.bz2
    MINICONDAROOT\Scripts\conda build gcc-arm
    MINICONDAROOT\Scripts\conda install MINICONDAROOT\conda-bld\win-64\gcc-arm-none-eabi-4.9.2015.q2.20150609-0.tar.bz2
    MINICONDAROOT\Scripts\conda build git
    MINICONDAROOT\Scripts\conda install MINICONDAROOT\conda-bld\win-64\git-2.5.0-0.tar.bz2


  .. note::

      * Respect the build order stated above
      * Be aware of overwrite warnings and respective yes/no questions that
        you might have to answer (with y)
      * Currently, the ``git`` build might open a graphical user interface.
        acknowledge.

* Upload the packages to the according channels on www.foxbms.org::

    scp \
    ~/applications/anaconda-linux-64/pkgs/gcc-arm-none-eabi-4.9.2015.q2.20150609-0.tar.bz2 \
    ~/applications/anaconda-linux-64/pkgs/doxygen-1.8.10-1.tar.bz2 \
    ~/applications/anaconda-linux-64/pkgs/breathe-4.0.0-py27_0.tar.bz2 \
    ~/applications/anaconda-linux-64/pkgs/cmake-3.3.0-0.tar.bz2 \
    admin@www.foxbms.org:/var/www/html/foxconda/channels/win-64

* logon to www.foxbms.org and run::

    foxconda_channels_index.sh 

Collect the package list
------------------------

* Deactivate the ``foxconda`` environment::

    deactivate

* Change to the ``foxconda\installer`` directory

* Run::

    MINICONDAROOT\python collect.py

* This will create an archive containing all packages and the dependencies
  that will be downloaded as ``data/condapackages-win-64.tar``

Building the installer
----------------------

* Install pyinstaller (using ``pip`` instead of ``conda``)::

    pip install pyinstaller

* Configure::

    ../tools/waf configure

* Build::

    ../tools/waf clean build

  .. note::

      clean


