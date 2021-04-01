#!/bin/bash

# This script creates a wheel distribution and uploads it to PyPi
#
# Requirements:
#
# twine https://pypi.python.org/pypi/twine (pip install twine)
# wheel https://pypi.python.org/pypi/wheel (pip install wheel)

SCRIPT_DIR="$( dirname "$( readlink "${BASH_SOURCE[0]}" )")"
cd ${SCRIPT_DIR} || exit
pip install -U twine wheel

repository=pypi

# Working directory
workDir=$PWD

# Dist directory
distDir=$workDir"/dist/"

# Clear contents of dist dir if it exists
if [ -d "$distDir" ]; then
    rm -r "$distDir"
fi

# Create wheel
python setup.py sdist bdist_wheel --universal
