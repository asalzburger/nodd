#!/bin/zsh
# Activate the local original-processor installation over the existing Spack view.
set -e
root=${0:A:h:h:h}
prefix="$root/software/build/key4hep/install"
[[ -f "$prefix/python/Gaudi/__init__.py" && -f "$prefix/bin/k4run" ]] || {
  print -u2 'Run make key4hep first'; exit 2
}
# Set paths inside the Spack-activated shell, after any setup helpers.
exec "$root/software/env/run.sh" /bin/zsh -c '
  prefix=$1; shift
  export PATH="$prefix/bin:$PATH"
  export PYTHONPATH="$prefix/python${PYTHONPATH:+:$PYTHONPATH}"
  export GAUDI_PLUGIN_PATH="$prefix/lib${GAUDI_PLUGIN_PATH:+:$GAUDI_PLUGIN_PATH}"
  export LD_LIBRARY_PATH="$prefix/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  # macOS strips DYLD_* when entering /bin/zsh. thisdd4hep.sh preserves the
  # activated view in DD4HEP_LIBRARY_PATH; restore it for DD4hep plugin discovery.
  export DYLD_LIBRARY_PATH="$prefix/lib${DD4HEP_LIBRARY_PATH:+:$DD4HEP_LIBRARY_PATH}${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
  export CMAKE_PREFIX_PATH="$prefix${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"
  exec "$@"
' key4hep "$prefix" "$@"
