#!/bin/bash
set -e
rm subs_manager_GUI || true
cython $1.py --embed
PYTHONLIBVER=python$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')$(python3-config --abiflags)
gcc -Os $(python3-config --includes) $1.c -o GUI/subs_manager $(python3-config --ldflags) -l$PYTHONLIBVER
rm $1.c
