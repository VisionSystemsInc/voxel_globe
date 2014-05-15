#!/bin/bash

#
# Sourcing this script will set up your environment to access all of
# the necessary tools for building and running the VSI NGA Metadata project.
#
# All dependencies will be initialized relative to the location of the script.
#
_script="$(readlink -f ${BASH_SOURCE[0]})"
 
#Delete the script name from $_script
export META_HOME="$(dirname $_script)"

echo Initializing environment Using NGA META HOME = $META_HOME

export PATH=$PATH:$META_HOME/../external/src/django/django/bin
export PYTHONPATH=$PYTHONPATH:$META_HOME/../external/src/django
