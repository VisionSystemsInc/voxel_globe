#!/usr/bin/env bash

source $(dirname ${BASH_SOURCE[0]})/np2r.env

export PS1="(npr): "

if [ "$#" == "0" ]; then
  echo "Starting bash session"
  bash --rcfile /dev/null
else
  "${@}"
fi
