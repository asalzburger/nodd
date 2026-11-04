#!/usr/bin/env zsh
# Source in a fresh zsh. Uses existing libraries without modifying shared installs.
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP
setup_spack
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/thisdd4hep.sh
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/geant4.sh
_nodd_truth_root="${${(%):-%N}:A:h:h:h}"
source "${_nodd_truth_root}/../nodd-software-layout/build/pyvenv/bin/activate"
source "${_nodd_truth_root}/../nodd-software-layout/build/acts/this_acts.sh"
unset _nodd_truth_root
