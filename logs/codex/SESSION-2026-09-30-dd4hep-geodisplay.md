# SESSION-2026-09-30-dd4hep-geodisplay — Correct geoDisplay loading

## Scope and selected request

The user tried geoDisplay on `build/pixel-compact-probe/pixel-barrel.xml` and
reported ROOT aborting while adding Z=18 to Air. This is a bounded follow-up to
PR #30, starting at `43a93e358a7d2dc3e6c78a4d82d1862880937347`.
Four unrelated untracked usage files were preserved.

## Findings and changes

The stale probe has eight element definitions; the maintained CMake compact in
`build/dd4hep/detector/compact/` has the corrected 98-element table. No material,
geometry or dependency change is required. The README now gives geoDisplay
commands and explains plugin discovery through DD4HEP_LIBRARY_PATH and the
platform dynamic-library path. Both the dylib and .components file reside in
`build/dd4hep/detector/`. The old ignored probe is left untouched.

The acts-spack preflight warned about changed setup/lockfile fingerprints. The
actual installed runtime was reverified with two successful checks: the full
validator without its explicit --library option, and geoDisplay -load_only on
the corrected compact. The latter reported 39388 nodes and clean exit0. The
interactive GUI was not opened, so rendered appearance is not claimed.

## Validation and delivery

README and dashboard evidence are updated in PR #30. Session/dashboard validation,
static-site build and whitespace checks are recorded in the paired JSON.
No DES-012 parameters or approval states were changed.

## Usage

Exact client per-turn input/output counters were unavailable; usage remains empty,
not zero. No subagents were used. The session summary is a repository aggregate,
not a measurement of this follow-up. Its output was checked after record validation.
