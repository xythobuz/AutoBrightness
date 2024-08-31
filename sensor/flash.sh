#!/bin/bash

# enter script directory
cd "$(dirname "$0")"

# upload to bootloader
./micronucleus/commandline/builds/x86_64-linux-gnu/micronucleus $1
