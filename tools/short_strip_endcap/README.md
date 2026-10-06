# Detailed short-strip endcap prototype

[DES-021](../../docs/design/DES-021-short-strip-endcap.md) is DRAFT. This standalone
factory is stacked on the selected tilted barrel (PR50); it is not wired into
production. It provides12 discs,12 removable petals/disc, five48/60/72/84/96-module
rings, shared strixel stacks, pickups, skins/foam, an embedded connected CO2
serpentine, three mounting seats, support frames, LV and HV/control buses,
outer boards/fans and cumulative endcap service transport cells.

FineU is tangential, coarseV inward radial, normal outward from IP. Negative
end placements use a proper x-axis half-turn. IDs use
`system:5,layer:4,petal:4,ring:3,module:4,sensor:1,x:-11,y:-10` (system4).
Per-disc IDs are stable within this new prototype, not old ideal-artifact IDs.

The first datum moves1295.5→1335mm for11.5mm collector clearance. Both layouts
remain coverage controls. The fixed710..783mm service trunk is never enlarged;
capacity includes barrel traffic while native transport mass contains only
endcap traffic. Overlaying both standalone service models would double-allocate
the corridor; integration needs a shared service replacement.

## Portable generation and controls

Use Python with NumPy; drawing also requires Matplotlib. Reuse the existing
project/ACTS Python environment rather than changing shared dependencies.

```sh
python3 -B tools/short_strip_endcap/model.py
python3 -B tools/short_strip_endcap/export.py
python3 -B -m unittest discover -s tools/short_strip_endcap -p 'test_*.py' -v
python3 -B tools/short_strip_endcap/check_layout.py
python3 -B tools/short_strip_endcap/draw.py --output build/short-strip-endcap/figures
```

Controls verify IDs/counts, signed frames, envelope limits, invalid first datum,
complete module/pickup separating axes, cooling-hole containment/separation,
and the conservative azimuth broad phase. Coverage compares116,640 sampled
vacuum helices against fixed original annuli/datums, and64 tracks against the
independent finite-plane solver. Missing ideal intersections are reported, not
removed from the denominator. Software PASS and engineering acceptance differ.

## DD4hep, ROOT and Geant4

Read the [acts-spack skill](../../skills/acts-spack/SKILL.md), run its preflight
and verify imports before using the runtime. On the tested node:

```sh
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP
setup_spack
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/thisdd4hep.sh
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/geant4.sh
cmake -S prototypes/short_strip_endcap -B build/short-strip-endcap/native-build -DBUILD_TESTING=ON
cmake --build build/short-strip-endcap/native-build -j4
ctest --test-dir build/short-strip-endcap/native-build --output-on-failure
python3 -B tools/short_strip_endcap/check_root.py \
  --root build/short-strip-endcap/native-build/native.root \
  --expected build/short-strip-endcap/native-build/compact/expected.json \
  --output build/short-strip-endcap/native-build/persisted.json
```

CTest audits every named sensitive/passive entity,4320 sensors,21,600 cell-centre probes,
passive radial tube axes, masses/constituents, zero overlaps at1e-5mm and120
actual ROOT material/navigation rays. ROOT persistence runs independently with
no factory load and native cm→model mm conversion. No ACTS conversion is claimed.

```sh
export DD4HEP_LIBRARY_PATH="$PWD/build/short-strip-endcap/native-build:${DD4HEP_LIBRARY_PATH:-}"
export DYLD_LIBRARY_PATH="$PWD/build/short-strip-endcap/native-build:${DYLD_LIBRARY_PATH:-}"
python3 "$(command -v ddsim)" \
  --compactFile build/short-strip-endcap/native-build/compact/short-strip-endcap.xml \
  --runType batch --numberOfEvents 1 --enableGun --gun.particle mu- \
  --gun.direction '0.195676,0.033589,0.980096' --gun.energy '10*GeV' \
  --physics.list FTFP_BERT --random.seed 42 \
  --outputFile build/short-strip-endcap/native-build/geant4-positive.root
python3 -B tools/short_strip_endcap/check_geant4.py \
  --root build/short-strip-endcap/native-build/geant4-positive.root \
  --log build/short-strip-endcap/native-build/geant4-positive.log \
  --native build/short-strip-endcap/native-build/native.json \
  --expected build/short-strip-endcap/native-build/compact/expected.json \
  --output build/short-strip-endcap/native-build/geant4-positive.json
```

Redirect DDSim stdout/stderr to the log named above. Repeat with negative gun z,
negative filenames and checker `--side -1` for the other end. The checker uses
saved particle relations to distinguish generated muon crossings from physical
secondary hits; only primary paths have the gun-plane analytical expectation.
Retain secondary hits. Raw XML, libraries, ROOT/events and runtime logs stay
ignored under `build/`; curated summaries and exact hashes are in
[the result report](../../docs/validation/DES-021/results.md).

```sh
python3 -B tools/short_strip_endcap/check_services.py \
  --expected build/short-strip-endcap/native-build/compact/expected.json \
  --output build/short-strip-endcap/services.json
```

## Effective representations and limits

ASICs, bumps and end boards are fixtures rather than qualified electronics.
Sensor guards/passive module layers, pickups, plates, tubes/coolant, buses and
seats are explicit solids. The fanout sheet and fan/trunk cells conserve
constituent volumes, density and approximate route length. Individual vias,
flex turns, connector penetrations, clamping bolts and cage connections remain
unqualified/omitted. Graph connectivity does not establish continuous solid
connectivity or installation clearance. Local10mm entry fillets require forming
review. No thermal, hydraulic, CTE, structural, ASIC, bandwidth or radiation
qualification follows from successful geometry construction.
