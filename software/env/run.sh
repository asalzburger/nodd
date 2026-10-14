#!/bin/zsh
# Bind to the existing node environment. Never install/concretize shared Spack.
node=$(hostname)
case "$node" in
  acts-mac-studio-01.cern.ch|acts-mac-studio-01) ;;
  *) print -u2 "Unsupported node: $node. This workflow is bound to acts-mac-studio-01."; exit 2 ;;
esac
setup=/Users/salzburg/cernbox/configs/acts/acts_setup.sh
view=/Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view
[[ -f "$setup" && -f "$view/bin/thisdd4hep.sh" && -f "$view/bin/geant4.sh" ]] || { print -u2 'Existing ACTS CI dependency environment is unavailable'; exit 2; }
source "$setup"
unset ACTS_SPACK_SETUP
setup_spack
[[ "${SPACK_ENV:-}" == /Users/salzburg/Documents/work/externals/ci-dependencies ]] || { print -u2 'Wrong Spack environment'; exit 2; }
source "$view/bin/thisdd4hep.sh"
source "$view/bin/geant4.sh"
set -e
export PYTHONDONTWRITEBYTECODE=1
exec "$@"
