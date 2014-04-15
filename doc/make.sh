#!/bin/sh
rm -f oictestGui*
sphinx-apidoc -F -o ../doc/ ../src/oictestGui
make clean
make html