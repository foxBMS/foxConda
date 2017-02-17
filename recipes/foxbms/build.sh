#!/bin/sh
#
# file:		build.sh
# date:		Wed Dec 02 11:28:32 CET 2015
# author:	Tim Fuehner <tim.fuehner@iisb.fraunhofer.de>
# $Id$
#
#!/bin/bash
mkdir -p "$PREFIX/Menu"
if [ $OSX_ARCH ]
then
	cp "$RECIPE_DIR/menu-osx.json" "$PREFIX/Menu"
	cp "$RECIPE_DIR/app.icns" "$PREFIX/Menu"
else
	cp "$RECIPE_DIR/menu-linux.json" "$PREFIX/Menu"
	#cp "$RECIPE_DIR/app.svg" "$PREFIX/Menu"
fi
$PYTHON setup.py install


