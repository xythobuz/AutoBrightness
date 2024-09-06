#!/bin/bash

# https://github.com/tenox7/ttyplot

# enter script directory
cd "$(dirname "$0")"

./lux.py | ttyplot -t "Brightness"
