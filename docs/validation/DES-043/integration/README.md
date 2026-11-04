# DES043 combined DD4hep integration — 2026-11-03

The human requested integration of the 703 mm short-strip redesign into the current working tracker and actual ODD TDR. The governing [DES043 amendment](../../../design/DES-043-short-strip-service-redesign.md) records this authorization. This is a working simulation prototype; no engineering sign-off or acceptance is granted.

The fixed implementation source is `d6c4d0ddfa9e14129a3f4c426fced7c4cee0dcc4`. All 12 new endcap discs and the 8,064 redesigned barrel modules are present: 4,752 endcap strixels, 46,682 complete-tracker sensitive planes and 54 signed groups. Standard combined system IDs 1–7/readout names are retained. Pixel and long-strip sensors are unchanged. The historical 46,250-plane physical baseline remains available through `--historical-short-strips` and its dated execution evidence is preserved.

The source includes explicit module/backing/core windows and graphite saddles, barrel U-turn cuts, 0.17 mm local copper, two cooling loops per endcap petal and the 717–781.5 mm shared trunk. Fans and trunk walls are partitioned into disjoint physical cells. Both ends have 1,008 power feeds, 1,584 independent optical groups, 864 leaf loops, 136 bulk pipe pairs and 720 boards. The conservative cable recipe includes every HV/control/shield constituent. Packing multipliers reserve space; they do not manufacture material. Unused corridor air is represented once.

The [compact results](summary.json) retain source/runtime/artifact hashes and aggregate tests. Raw generated XML, expected entity maps, native inventories, Gen3 JSON, ROOT files and run logs remain ignored under `build/`. No event samples or bulky reference-run files belong in this PR.

## Executed checks

| Check | Result |
| --- | --- |
| Full DD4hep/ROOT | PASS; 636,460 placements, 46,682 unique sensitive IDs, zero overlaps/extrusions at 1e-5 mm |
| Sensitive transforms | All 46,682 match; maximum centre residual 5.70×10⁻¹³ mm |
| Strixel cells and finite geometry | 64,080 cell round trips and 180,288 backing/cold-window/pipe-contact probes |
| Supplementary payload | PASS; 617,018 exact physical solids, 1,316 native material definitions, 200 protected sources, 16 XML and 8 expected records; maximum elemental fraction residual 1.12×10⁻¹⁶ |
| ACTS Gen3 | 46,682 planes / 54 groups / 120 volumes; complete native JSON round trip |
| Straight navigation | 128 seed-42 tracks; all seven systems; 10–27 sensitive and at least 25 portal crossings per track |
| Geant4 construction/transport | Three seed-62043003 geantinos; three saved events / one run |
| TDR | 32-page report and 28-page extract compiled, inspected and published at 80a6c998 |

The supplementary audit re-executes the full contact contract and binds the same five libraries to the native PASS report. Only the root Air container is exempt from the physical-solid inventory; the two explicit beampipe solids are bridged from their pinned factory/XML contract. The compact summary is 26 KB. ROOT point generation took 1,372.04 s and candidate checking 81.3254 s, with no tolerance/sampling change. These are observed timings on this node, not runtime guarantees.

## Reproduce

Run the repository's acts-spack node preflight and verify DD4hep/ROOT/Geant4 runtime imports before using the local environment. The executed runtime is DD4hep 1.38, ROOT 6.40.04, Geant4 11.4.3 and Python 3.14.5. Recorded setup/lock fingerprints had changed; actual capabilities were rechecked. No shared dependencies were installed or rebuilt.

In the verified Spack/DD4hep/Geant4 shell (the absolute setup paths are node-specific):

```sh
cmake -S . -B build/short-strip-redesign/combined-native -G Ninja -DBUILD_TESTING=ON
cmake --build build/short-strip-redesign/combined-native --target nODDPixelBarrel nODDBeamPipe nODDShortStripBarrel nODDShortStripEndcap nODDLongStrip Components_nODDPixelBarrel Components_nODDBeamPipe Components_nODDShortStripBarrel Components_nODDShortStripEndcap Components_nODDLongStrip --parallel 5
python3 -B tools/tracker_dd4hep/export.py --output build/short-strip-redesign/combined-native/detector/tracker
export DD4HEP_LIBRARY_PATH="$PWD/build/short-strip-redesign/combined-native/detector:${DD4HEP_LIBRARY_PATH:-}"
export DYLD_LIBRARY_PATH="$PWD/build/short-strip-redesign/combined-native/detector:${DYLD_LIBRARY_PATH:-}"
python3 -u -B tools/tracker_dd4hep/validate.py \
 --compact build/short-strip-redesign/combined-native/detector/tracker/tracker.xml \
 --expected build/short-strip-redesign/combined-native/detector/tracker/expected.json \
 --library-dir build/short-strip-redesign/combined-native/detector \
 --output build/short-strip-redesign/combined-native/native.json
python3 -u -B tools/tracker_dd4hep/audit_payload.py \
 --compact build/short-strip-redesign/combined-native/detector/tracker/tracker.xml \
 --library-dir build/short-strip-redesign/combined-native/detector \ --native-report build/short-strip-redesign/combined-native/native.json \
 --source-revision d6c4d0ddfa9e14129a3f4c426fced7c4cee0dcc4 \
 --output build/short-strip-redesign/combined-native/payload-audit.json
```

Native overlap tolerance remains 1e-5 mm, with ROOT's default point sampling (no user seed). Source screens and producers are deterministic. Keep geometry sources and generated inputs fixed during execution. The first strict-shell attempt exited on setup diagnostics before generation; strict mode was moved after successful runtime activation. The initial ACTS attempt lacked `.components` registries; explicitly building the five registry targets corrected it.

Activate `acts run acts-nodd` and its installed Python environment, then:

```sh
python3 -u -B tools/tracker_dd4hep/export_gen3.py \
 --build-dir build/short-strip-redesign/combined-native \
 --output-dir build/short-strip-redesign/combined-native/gen3
```

Record and audit 128 seeded straight navigation probes as a separate smoke check:

```sh
python3 -u -B tools/tracker_dd4hep/navigation_smoke.py \
 --nodd-dir "$PWD" --build-dir "$PWD/build/short-strip-redesign/combined-native" \
 --output build/short-strip-redesign/combined-native/navigation --tracks 128
python3 -B tools/tracker_dd4hep/check_gen3.py \
 --report build/short-strip-redesign/combined-native/navigation/surfaces.json \
 --expected build/short-strip-redesign/combined-native/detector/tracker/expected.json \
 --output build/short-strip-redesign/combined-native/navigation-source-comparison.json
python3 -B tools/tracker_dd4hep/check_navigation.py \
 --directory build/short-strip-redesign/combined-native/navigation --tracks 128 \
 --output build/short-strip-redesign/combined-native/navigation-check.json
```

The latter checker requires uproot/awkward from the documented analysis environment. It checks saved summaries/steps, source IDs and all seven systems. Seed 42, 10 GeV muons, η uniform in −4..4, StraightLineStepper, no energy loss/scattering. This is software navigation, not a field/acceptance or tracking-performance study. The maintained script follows the ACTS example flow and is retained with its MPL-2.0 header.

This checks every source plane and a complete native JSON serialization round trip. Installed binary/module hashes identify the executing ACTS runtime. The sister checkout's current source HEAD is not substituted for a compiled-binary revision.

The Geant4 smoke command in the same DD4hep/Geant4 shell is:

```sh
python3 "$(command -v DDSim)" \
 --compactFile build/short-strip-redesign/combined-native/detector/tracker/tracker.xml \
 --runType batch --enableGun --gun.particle geantino --gun.energy '1*GeV' \
 --gun.direction '1 0 1' --numberOfEvents 3 --physics.list FTFP_BERT \
 --random.seed 62043003 \
 --outputFile build/short-strip-redesign/combined-native/geant4-smoke.root \
 > build/short-strip-redesign/combined-native/geant4-smoke.log 2>&1
```

In a fresh shell with uproot available in the documented analysis environment, curate aggregate evidence and check it without the local run payloads:

```sh
python3 -I -B tools/tracker_dd4hep/curate_des043.py --build-dir build/short-strip-redesign/combined-native
python3 -B tools/tracker_dd4hep/curate_des043.py --check
python3 -B -m unittest discover -s tools/tracker_dd4hep -p 'test_*.py' -v
python3 -B -m unittest discover -s tools/short_strip_redesign -p 'test_*.py' -v
python3 -B tools/short_strip_redesign/verify.py
python3 -B tools/tracker_dd4hep/verify_baseline.py
```

The [publication receipt](../../../publication/short-strip-services-2026-11-03/README.md) retains the separate actual TDR source identity and reproducible figures. Current [layout inputs](../../../layouts/tracker-baseline-des043.json) likewise distinguish the new tracker overlay from historical FCAL/Si-W/LAr validation geometry.

## Scope and open qualifications

General intersecting CSG volumes have explicit bounds, not a falsely exact total mass. The analytical changed-component saving is −114.6 kg with no cable-insulation credit (−287.8 kg under the original insulation proxy); no ASIC/backing-removal/optical savings are credited. That ledger conservatively retains 6.48 power-bundle metres beyond the integrated joins. A complete directional material comparison is still required to claim the full tracker material benefit.

The adverse complete thermal screen leaves only 0.333 K to the −20 °C sensor limit. Actual ASIC, 8 mm cable package, cold contact/bond conductivities, upstream leakage path, irradiation, sensor bow and two-phase hydraulics remain unqualified. Existing 2 mm truth/GBTS/ttbar results used the preceding physical geometry. The current tests establish geometry construction, identifiers, interfaces, conversion and transport only; they do not establish new tracking efficiency/fake rates or field navigation.
