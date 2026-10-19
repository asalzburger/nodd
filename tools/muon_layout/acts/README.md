# ACTS chamber-face propagation — PROTOTYPE

This isolated DES040 validation uses the fixed 1,560 chamber prisms and the
retained joint solenoid/toroid map. It does not integrate a detector component.
Read the [method amendment](../../../../docs/design/DES-040-muon-chambers-frame.md#pr90-acts-propagation-amendment-2026-10-19-before-implementation),
[engine contract](README-engine.md), and
[ACTS rebuild evidence](../../../../docs/validation/DES-040/acts-propagation/rebuild.md).

Only the two large faces of a chamber count as provisional segment proxies.
Sides remain in the raw boundary-event arrays for navigation checks. Six unique
large faces and three stations with contiguous same-chamber opposite-face pairs
are separate observables. The 30 mm inactive-border proxy is reported separately.

All momenta are total **local entrance momentum**, not pT or IP momentum.
The 2.65 GeV stress point comes from the earlier central 5 GeV IP mean-loss
estimate; it is not a universal muon threshold. The entrance is a virtual closed
cylinder, R=4.35 m, half-z=6.50 m, including both caps. Seed directions are radial,
10 micrometres beyond that surface. No upstream material transport, scattering,
chamber response, fitting or efficiency is simulated.

The native tracking geometry contains all finite chamber volumes/portals.
The primary **surface-audit** navigation targets supporting surfaces with native
ACTS EigenStepper/Navigator, then checks actual finite faces at each native root.
It includes coplanar owners. This is a boundary audit, not qualification of native
portal transitions through all chambers. The original finite-portal algorithm
missed an analytically known curved-edge entry; that negative control is retained.
No polyline postprocessing supplies the primary hit positions.

## Reproduction

Use an existing verified ACTS installation and its dependency environment. The
local node requires the repository's acts-spack preflight and prescribed setup.
The user-requested rebuild kept the full existing github-ci feature set and
regenerated the installed dependency pins; do not disable plugins or fill field
masks to bypass a failing control. Configure in an ignored task-owned directory:

```sh
cmake -S tools/muon_layout/acts -B reference/cache/pr90-acts/build -G Ninja \
  -DCMAKE_PREFIX_PATH=/path/to/verified/acts/install -DCMAKE_BUILD_TYPE=Release
cmake --build reference/cache/pr90-acts/build --parallel 2
python3 -B tools/muon_layout/acts/prepare.py --work reference/cache/pr90-acts
```

Run the native controls before the scan. Their CLI is described by
`python3 -B tools/muon_layout/acts/controls.py --help`. Use
`reference/cache/pr90-acts/build/nodd-muon-propagate` as the executable and write
the executed control record to `docs/validation/DES-040/acts-propagation/controls.json`.
The scan refuses an unsuccessful control record or a changed executable.

```sh
python3 -B -m tools.muon_layout.acts.run --work reference/cache/pr90-acts \
  --executable reference/cache/pr90-acts/build/nodd-muon-propagate \
  --output reference/cache/pr90-acts/production \
  --controls docs/validation/DES-040/acts-propagation/controls.json --workers 4
python3 -B tools/muon_layout/acts/analyze.py --work reference/cache/pr90-acts \
  --run reference/cache/pr90-acts/production \
  --output docs/validation/DES-040/acts-propagation
python3 -B tools/muon_layout/acts/draw.py docs/validation/DES-040/acts-propagation \
  docs/validation/DES-040/acts-propagation
```

The five momenta and two charges share seeded directions. The phi/eta display
has one solid-angle-jittered ray per cell over eta −3 to +3. Its weights and
finite display range are explicit. A separate 4,096-direction full-sphere sample
per case supplies the untruncated 4pi denominator. This is a finite sampling
study, not a converged efficiency map. Every generated track remains present.
Strict masked/outside field queries fail; they never become zero field.
Proven threshold crossings before a later failure remain a lower-bound pass;
unfinished events also contribute to the possible upper bound. These bounds
describe unfinished-event uncertainty, not a confidence interval.

`tracks.npz` preserves entrance seeds, momenta, charge, status and counters.
`hits.npz` preserves every returned native boundary position, path, direction,
owner and uint64 geometry ID; never parse those IDs as float64. Task-local raw
CSVs and native geometry exports retain hashes in the execution record.
Captured-artifact checks can run without ACTS; they do not claim to rerun native
propagation. Fresh scientific execution requires the native controls above.
