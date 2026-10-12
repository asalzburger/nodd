# ACTS nODD examples — initial DD4hep material recording

- Date:2026-10-06; bounded software task requested by the user.
- Model: current preliminary DES019 pixel barrel and trimmed mixed endcaps.
- ACTS deliverable:555c66e71d0639665c2fa3d5574a0fe7f3f62cde on codex/nodd-examples.
- Exact input, source, installed artifact and output hashes: [implementation.json](implementation.json).

The new Examples/Nodd component supplies the DD4hepNoddDetector C++ class,
acts.examples.nodd bindings/path helper, and Scripts/nodd_material_recording.py.
The helper locates the maintained external compact and factory library, checks
paths, explicitly loads the factory and preserves DD4hep component search paths.
The script follows the existing ACTS neutral-geantino event-generation,
HepMC3 conversion, Geant4 recording and ROOT writer pipeline. Geometry is owned
by nODD. No ODD material map or new physics parameter is introduced.

The current compact's exported inventory is5362modules/11806activechips. Its
combined configuration and recorded source hashes match the current nODD
checkout; positive disc datums are615,795,1046,1333,1645,1977,2328,2692,3070mm.
The recorded export/native identities are retained separately from this task's
ACTS source commit and the parent record's enclosing commit.

## Actual checks

All pre-commit hooks passed after automatic task-file formatting. acts build
acts-nodd4 passed and installed the header/library/binding/helper/script. The
full C++ suite passed385/385tests in75.90s. Six focused Python tests passed
in16.42s, including native DD4hep loading and one event with eight Geant4
material probes. The resulting ROOT tree has eight entries with finite positive
radiation-length totals. That actual output is retained in the primary nODD
checkout's ignored build/acts-nodd-nodd-examples/nodd-material-smoke.root.

Spack preflight reports changed historical setup/lock fingerprints. Initially,
activating only Spack and the venv did not expose ACTS; correct acts run acts-nodd
activation verified the installed Python environment and ROOT/DD4hep/Geant4
imports. The standard ACTS build helper recreates its existing venv and installs
its configured Python prerequisites. Existing user edits in ACTS were included
in the working environment and preserved byte for byte, without being staged
or committed in this deliverable. This execution was initial355ea684 plus the
new source and those existing edits, not a clean future-commit run.

## Reproduction and boundary

Activate acts run acts-nodd, then run Examples/Nodd/Scripts/nodd_material_recording.py
with --nodd-dir pointing at the built nODD checkout. --build-dir and --compact
accept explicit overrides; --events/--tracks/--seed, eta/phi bounds, output stem
and material-track collection are configurable. The ACTS Examples/Nodd/README.md
contains the full commands. Its ignored _work_diffs/nodd-examples.md and patch
retain the focused review diff.

This first adapter loads DD4hep/TGeo and supplies Geant4 detector construction.
ACTS tracking-geometry conversion is a separate later increment. Eight straight
material probes establish software plumbing, not physics acceptance, a converged
material map or engineering qualification. DES016–019 remain DRAFT, with their
existing engineering/coverage limitations. No design sign-off is inferred.
