---
name: acts-spack
description: Activate and verify the node-specific ACTS Spack environment for DD4hep and Geant4 builds, runtime imports, datasets and source access. Use before relying on setup_spack or these local preinstalled dependencies; warn when the current node or required capability is unavailable.
---

# ACTS Spack environment

Use the user's existing `acts_setup.sh` and `setup_spack` workflow. The verified
nodes and capability boundaries are in [references/nodes.json](references/nodes.json).
Do not assume that the same paths or installations exist on another node.

Before a dependent request, run `python3 <skill-dir>/scripts/preflight.py`.
For source-level work add `--require-sources`. Report any warning to the user
before attempting dependent work. An unknown node is **unverified**, not proof
of a missing installation; inspect its user-provided setup and verify it before
adding it to the registry. A known node with missing files is unavailable; a
changed setup or lockfile requires re-verification. Permission restrictions are
distinct from a missing installation. Do not quietly substitute another toolkit.

Read [references/workflow.md](references/workflow.md) for the verified setup,
runtime/source checks and optional C++ smoke test. Run activation and dependent
commands in the **same fresh zsh process**: environment changes do not survive
separate tool calls. `setup_spack` sets its guard even after inner failures, so
the guard and function exit status alone do not establish successful activation.

The registry's preflight checks only files and fingerprints; rerun the relevant
Spack/runtime checks before claiming current availability. Libraries/headers,
Python runtime, datasets, staged full sources and simulation readiness are
separate capabilities. In particular `spack location -s` prints a potential
stage path even when absent; use `--source-dir` and inspect actual source files.

Inspection does not authorize `spack install`, `concretize`, `stage`, updates,
source downloads or changes to shared installations. Use the existing environment
for the requested work; source acquisition or dependency changes are separate
tasks. The sourced script defines clone/build/clear helpers too; do not invoke
those as part of environment discovery. Keep the external setup/configuration
out of Git and do not collect credentials or a complete environment dump.

Record newly verified nodes with date, exact hostname, platform, setup and
lockfile fingerprints, installed package hashes and separately tested
capabilities. Keep untested nodes unknown and preserve earlier evidence in Git.
