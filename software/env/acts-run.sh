#!/bin/zsh
# Called through env/run.sh, which activates the existing Spack dependencies.
set -e
acts_build=$1
shift
[[ -f "$acts_build/this_acts.sh" ]] || { print -u2 'Build the local software first'; exit 2; }
source "$acts_build/this_acts.sh"
exec "$@"
