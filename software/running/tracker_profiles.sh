#!/bin/zsh
# Activate the existing node runtime; dependency installation is a separate step.
set -e
root=${0:A:h:h:h}
setup=${ACTS_SETUP_SCRIPT:-/Users/salzburg/cernbox/configs/acts/acts_setup.sh}
runtime=${ACTS_RUNTIME_NAME:-acts-nodd}
source "$setup"
acts run "$runtime"
exec python "$root/tools/tracker_propagation/run.py" "$@"
