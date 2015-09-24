============================================
foxConda installer generation infrastructure
============================================

Package generation
------------------

Create a new environment called “foxconda”::

    conda create -n foxconda sphinx

In so doing, the package ``sphinx`` and all its dependencies will live in
the initial “foxconda” environment. 

All packages intended for use with foxBMS should be placed into this
environment. Thus for the package building, it is best practice to switch to
that environment. On Linux::

    . activate foxconda

On Windows::

    activate foxconda

Now start by installing  

Package collection
------------------

``collect.py``

maintains a list of requirements, fetches the packages accordingly and
copies them into the ``pkgs`` sub-directory of this

``install.py``

Script that is wrapped into and executed by the PyInstaller executable.




PyInstaller
-----------

``foxcondainstall``

    * ``condapackages.tar``
      Archive containing all minimum requirement packages for foxConda.
      After installation, a bare-bone MiniConda Python environment will be
      available.

    * ``foxconda-deps-0.1-0.tar.bz2``
      Meta package containing all dependencies required for foxBMS.
      Installing this package will resolve the dependencies by installing
      the respective packages. Both the custom channels and the foxBMS.org
      channels are required for the resolution.

    * ``LICENSE-ANACONDA.txt``
      Anaconda license. :FIXME: should be supplemented with the according
      foxBMS license terms. Preferably in an additional file.


  

