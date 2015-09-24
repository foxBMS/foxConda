mkdir Scripts
move doxygen.exe Scripts
move doxyindexer.exe Scripts
move doxysearch.cgi.exe Scripts
xcopy * %PREFIX% /E /C
echo "bat done"
