# Verified workflow

Node: `acts-mac-studio-01.cern.ch`, Darwin arm64, verified 2026-09-22.
Other nodes have not been tested. The machine-readable registry is
[nodes.json](nodes.json); rerun preflight before relying on its snapshot.

Run the following in one fresh zsh process. Sourcing only defines helpers;
`setup_spack` activates the Spack environment. The additional DD4hep setup is
needed for `DD4HEP_LIBRARY_PATH` and its Python runtime.

```sh
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP  # Fresh subprocess only; force actual verification.
setup_spack
spack env status
spack find --format '{name}@{version} /{hash:7} {prefix}' dd4hep geant4
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/thisdd4hep.sh
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/geant4.sh
python3 -c 'import dd4hep; import DDG4; print("DD4hep/DDG4 imports OK")'
geant4-config --version
geant4-config --check-datasets
```

Observed: DD4hep 1.37 with DDG4, Geant4 11.4.1, Python 3.14.5, Spack
1.3.0.dev0 at `c2e5f49c353f79e007386d5bf734980d6a02b105`. The activated
environment is `/Users/salzburg/Documents/work/externals/ci-dependencies`;
its checkout revision was `58492cdd83fd15aef922327217599d13ff45cd11`.
Use the lockfile fingerprint and package hashes, not checkout revision alone,
to identify the actual installed environment. Twelve Geant4 datasets report
installed despite the package's `~data` variant: they were supplied separately.
Presence checks are not checksums or proof of full simulation readiness.

The sandbox denied `sysctl` CPU detection while sourcing the setup. A normal
authorized subprocess succeeded. Treat this as restricted execution, not a
missing package. The helper itself exports its success guard unconditionally;
verify `spack env status`, actual installed specs and runtime checks.

## Libraries versus full sources

```sh
spack location --install-dir dd4hep
spack location --install-dir geant4
spack location --source-dir dd4hep
spack location --source-dir geant4
```

Both source-dir queries failed: full source trees are **not currently staged**.
Installed headers, CMake packages, libraries and Spack recipes are present, but
do not equate them with complete source checkouts. `spack location -s` is a stage
path query, not a source-availability test. No source download or staging was
performed. A source-level task needs separate acquisition or a verified checkout.

## Optional compile/link smoke test

After activation in the same shell, from the nODD checkout:

```sh
cmake -S skills/acts-spack/scripts/smoke -B reference/cache/spack-skill/build -G Ninja
cmake --build reference/cache/spack-skill/build --parallel 2
reference/cache/spack-skill/build/spack-smoke
```

For an installed skill copy, substitute its `scripts/smoke` directory for `-S`
and use a task-owned writable build directory. This compiled and ran against
DDCore, DDG4 and Geant4, obtained a DD4hep Detector and a Geant4 NIST silicon
material. It does not construct nODD or transport events. CMake emitted developer
policy warnings and a CLHEP directory mismatch; the view and original
`CLHEPConfig.cmake` resolve to the same file. No warning suppression or shared
installation modification was needed. Keep build results out of the skill folder.


## Verification refresh, 2026-10-14

The software-layout migration reverified the same node and existing CI Spack
environment after setup/lock fingerprints changed. The current registry records
DD4hep1.38 and Geant4 11.4.2;12 datasets and DD4hep/DDG4 imports pass. Standalone
nODD factories, native/Gen3 comparison, an8-track Geant4 material-recording smoke
and a native nodehammer build were exercised. The simulation observation is a
smoke test, not a detector-response/performance certification. The installed
personal skill copy is independent; this refresh changes repository records only.
See logs/codex/SESSION-2026-10-14-software-layout.md from the repository root for
commands, stage revisions and exact check scopes. The older dated results above
remain historical evidence; shared dependencies were not modified.
