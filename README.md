===============================
Building the foxConda Installer
===============================

:author:    The foxBMS Team (Tim Fühner <tim.fuehner@iisb.fraunhofer.de>)
:version:   0.5

The *foxBMS* project comes with its own Python distribution, called
*foxConda*. Python is a modern, interpreted programming language whose
great popularity is still increasing, also owing to the multitude of
libraries that are available for virtually any application. In combination
with an easy-to-use distribution, like Anaconda_, Python constitutes an
ideal development platform. We have therefore decided to also employ it as
a software development toolkit (SDK) for *foxBMS*.
For an even improved user experience and maintainability, we are not only
providing Python programs and packages to get you started with *foxBMS*, we
have additionally devised a dedicated, comprehensive distribution, which
includes all the packages you need. It is based on Anaconda and is hence
fully compatible with it. 

.. _Anaconda: http://www.anaconda.org


Creating a foxConda distribution and building the installer
-----------------------------------------------------------

You can find the configuration files required to build a standard foxConda
distribution and its installer in the ``foxconda-makeinstaller``
subdirectory of the ``foxconda`` repository. In addition, the list of
packages that are to be included in the ”bootstrap” foxConda distribution,
is specified in the file ``bootstrap/packages.yaml`` in the same
repository. You will also need the ``scripts/bootstrap.py`` script, and a
running Python environment (version 2.6 or higher) and ``yaml`` support [#FIXME]. 
Furthermore, make sure you have a working internet connection since the
bootstrap process will automatically download all required package and
source files.

Unless you would like to customize or modify it, no changes are required,
and you can simply issue the build commands.

Simplified build
++++++++++++++++

1. If not done so, clone ``foxconda`` and change into the working
   directory::

       git clone https://github.com/foxBMS/foxconda

2. Issue::

       python scripts/bootstrap.py -p bootstrap/packages.yaml <INSTALLDIR>

   Here, it is aѕsumed that the ``python`` command is in your system path.
   ``INSTALLDIR`` is the path to the bootstrap *foxConda* installation
   directory. It will be used to collect the third-party packages and build
   the *foxBMS* modules. After the *foxConda* installer has been built, it
   can be safely removed.

   The file containing the list of packages is specified using the ``-p``
   option. As shown above, you can simply use the provided list, located in
   the ``bootstrap`` directory.

   Further options of the ``bootstrap.py`` script are shown when issuing::

       python scripts/bootstrap.py --help
   
3. Afterward, your *foxConda* bootstrap directory is ready. For the next
   step, use Python from this bootstrap distribution by activating it::

       . <INSTALLDIR>/bin/activate root

4. Change into the ``foxconda-makeinstaller`` directory and execute::

        python makeinstall.py all

The *foxConda* installer will be situated in the ``dist`` subdirectory.


Step-by-step build
++++++++++++++++++

1.  Bootstrap the initial *foxConda* installation, as shown in the previous
    simplified build steps instructions (1.–3.).

2.  Change into the ``foxconda-makeinstaller`` directory.

3.  Fetch the repository file, which represents the package list of the
    bootstrap installation::

        fcgetrepository file:///<INSTALLDIR>

    The package list will be stored in a file called ``repodata.json``.

4.  Generate the payload of the installer, i.e., an archive containing all
    packages the *foxConda* distribution is to contain::

        fcmakepayload repodata.json

    The payload will be stored in a file called ``payload.tar``.

5.  Generatea the installer, issuing::

        fcmakeinstaller installer.yaml

    The file ``installer.yaml`` contains the configuration for the
    installer. The generated installer will be located in the ``dist``
    subdirectory.


Customizing foxConda
++++++++++++++++++++

To create a custom foxConda distribution and the according installer from
scratch, you have to provide a number of customization and configuration
files. 

``bootstrap/packages.yaml``   This file contains the list of packages
    that are to be installed in the bootstrap environment. It contains two
    sections: (1) ``installpackages``: These packages will be fetched from
    Anaconda or other publicly available channels; and (2)
    ``buildpackages``: These packages will be built, and their recepies are
    expected to be located in the ``recepies`` subdirectory (or another
    location to which the ``--recipesdir`` option of
    ``scripts/bootstrap.py`` points).

    In addition, in the section ``channels``, you can specify custom
    channels for specific packages.

``recipes``    This directory contains all the recipes for the *foxBMS* or
    their support packages.

``foxconda/makeinstaller``    This directory contains the configuration
    files required for the installer generation:

    ``installer.yaml``    This is the configuration file, which specifieѕ
        the behavior and appearance of the installer. It allows you to set
        logos, welcome screens, messages, version numbers and programs to
        be launched after the installation has finished. See the provided
        example configuration file for further details.

        .. note:

           The names of the following files are specified in the
           ``installer.yaml`` file and may differ if you have chosen
           to give them different names.

    ``app.ico``, ``app.icns``, ``app.svg``      These are the installer
        icons for Windows, MacOS and Linux, respectively.

    ``installer.png``   This is the welcome image of the installer

    ``anaconda.LICENSE``, ``LICENSE``   These are the license files for the
        Anaconda Python distribution, which we supply since *foxConda* is
        derived work, and the *foxConda* license. You mileage may vary, but
        we strongly encourage you to leave the licenses as are and simply
        add your specific license file if required.

    ``install.py``  This script is required by the *conda* installation
        process. Unless you are certain about what you are doing, it is
        best to leave it as it is.

    ``postinstall.py``   This script will be executed after *foxConda* was
        successfully installed. It can be used to execute post-installation
        triggers.

    ``windowsexedetails.txt``    This file is used to supply the Windows
        executuable of the installer with version and credit information.

Overview
--------

.. image:: doc/overview.svg
   :width: 1000 px
