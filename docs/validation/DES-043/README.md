# DES043 — redesigned short strips and services

- Status: DRAFT / PROTOTYPE; source screens, not hardware acceptance.
- Date: 2026-11-02.
- Candidate: **SS-2MM-SVC-01**, governed by [DES043](../../design/DES-043-short-strip-service-redesign.md).
- Input baseline: merged PR109 `b564308fe2e76da42d0d62c6ba33f9c76876119c`.
- Human instruction: redesign short strips/cables/cooling, reduce endcap gap and
  material; follow-up authorizes module redesign for703mm coverage.

## Result and boundaries

Five rings at289.5/381.25/473/564.75/656.5mm retain the sensor outline and add
432 endcap sensors. The finite active envelope extends to704.909mm; the sampled
full-azimuth target is243.5..703mm. The physical radial gap to unchanged long
silicon is82.335mm, versus114.758mm. The full design and qualifications are in
[DES043](../../design/DES-043-short-strip-service-redesign.md).

The package specifies10mm² LV conductors,8mm complete cable,0.17mm local rails,
0.35mm spreader, insulating TIM and central16x60mm direct pipe saddles with8mm maximum thermal
path. Cable/ASIC feasibility and cold properties remain requirements. Two
circuits per petal retain tube dimensions. The nominal/adverse analytical
screens pass; the no-power-scaling stress case fails electrical, thermal and
enthalpy requirements. A finished8mm cable with all conductors/insulation is a
critical unqualified dependency of the narrower717..781.5mm tray.

The scoped material ledger gives−287.8kg, or **−114.6kg with no cable-insulation
saving credited**. It retains added sensors, full thermal insert thickness,
additional cooling and5g/module passive reserve, and takes no ASIC mass credit.
These estimates depend on the inherited effective cable composition and are
not a complete tracker mass or material map. The Cu-only η figure excludes
all other tracker components. Existing reconstruction results use the previous
geometry and cannot validate this proposal.

## Reproduce

From the repository root, Python≥3.11, standard library only:

```sh
python3 -B -m unittest discover -s tools/short_strip_redesign -p 'test_*.py' -v
python3 -B tools/short_strip_redesign/model.py --output /tmp/DES043-summary.json
python3 -B tools/short_strip_redesign/verify.py
```

The model is deterministic and needs no random seed, event sample or native
runtime. It imports the historical source models without altering them; their
six source-file hashes and full baseline revision are pinned in inputs.json
and retained in summary.json. Producer/diagnostic/input hashes are recorded.
Numerical replay uses relative1e-11/absolute1e-10 tolerance for cross-platform
floating-point differences. There is no statistical uncertainty; the relevant
uncertainty is the explicit engineering assumptions and adverse controls.

Plot with the versions/install recipe in
[the tool guide](../../../tools/short_strip_redesign/README.md):

```sh
build/short-strip-redesign/plot-venv/bin/python tools/short_strip_redesign/plot.py --summary /tmp/DES043-summary.json --output /tmp/DES043-figures
```

Execution used the existing ignored sibling study venv:
`../nodd-gen3-material-mapping/build/truth-tracking-baseline/analysis-venv/bin/python`.
Versions: NumPy2.4.6, Matplotlib3.11.2, unrooted0.1.0rc1 at
`728465dce0c5cd5b876e67392e3858de6e982d05`. `figures/manifest.json` binds producer,
input summary and all10PNG/PDF hashes. Inspect plots visually after regeneration;
rendering can differ with font/runtime versions. No event-level or large run
artifact is required or committed.

## Checks and controls

| Check | Actual evidence / limits |
| --- | --- |
| Population and finite bounds | 4,752 EC sensors,8,064 barrel; exact rectangle corners and edge-foot minima; unchanged long geometry |
| Finite-plane coverage | 25,920 straight rays:6positive stations ×3vertices(z0=−150/0/+150mm) ×1,440midpoint phis; mirrored-end symmetry; zero sampled holes through703mm;0.610mm minimum outer margin |
| Independent interface screen | SysArch input, exactb564308, tested earlier91.5mm candidate at1,440and2,880phis; new91.75mm result recomputed by coordinator |
| Electrical adverse | Warm1.4ρ, constant-power current bound11V; includes0.15V connector/protection budget; worsttotal0.96206V;0.15mm rail and8mm² feeder counterexamples fail |
| Cumulative service area | All12sectors incl. barrel +6discs/end, independent optical counts and doubled EC cooling; worst0.96184; old collector throat,725mm tray and10mm cable controls fail |
| Planar two-loop routing | Ordered4ports, actual arc/straight lengths;0.5mm sampling lower-bound interloop surface separation1.843mm. Same-loop source checks also pass; full solid/support clearances require native geometry |
| Thermal adverse | Requiredκ/TIM/contact/boiling values; direct saddle8mm; distributed leakage-corner allowance; EC−20.333°C. No-scaling control fails |
| Cooling | Enthalpy only, no pressure-drop/dryout qualification; nominal/adverse pass, stress control fails |
| Material | Explicit conductor volumes + additions; empty envelope not mass; no ASIC/optical/backing-removal savings; no-insulation-credit sensitivity retained |
| Portable unit tests | 20 model/native requirements/negative controls; see session journal for final run |
| Figure QA | Five figure families renderedPNG/PDF with unrooted/Matplotlib; coordinator inspected allPNG layouts |

The first test of a rounded newly calculated gap literal failed at8e-7mm; the
literal was corrected to the exact finite-edge result. No approved tolerance
was relaxed. This is a test-authoring correction, not a physical discrepancy.

## Native module prototype and follow-up

The user subsequently authorized the module redesign itself. The inherited6..24degree loop missed edge-module lands, independently confirmed
by PhysVal at895b9e1. It is superseded by3..27degree arcs, R10stadiumhairpins
and onecentral16x60pad. All33assigned-module contacts are explicitly tested.
Native exporter and explicit window/saddle construction are implemented under
`DES043-SoftEng-02`. The fixed476826f geometry audit passed792actualsensors,
7200contact/window probes andzerooverlaps at1e-5mm; its original revision is
retained. Final evidence is bound to the actual rerun source revision in
[native-summary.json](native-summary.json). Full tracker
integration, Geant4 material mapping and ACTS/reconstruction comparison remain
separate until the new geometry is built and checked.

The preflight warned that the recorded Spack setup/lock changed. Runtime was
then directly reverified: DD4hep1.38 `/3yd4hz3`, Geant4 11.4.3 `/wfg55xi`,
DD4hep/DDG4 imports and12datasets available. The setup emitted sandbox `sysctl`
and shell-detection warnings; these did not prevent imports. No shared dependency
was rebuilt or changed and no staged upstream sources are claimed.

## Native reproduction recipe

After the documented acts-spack preflight and runtime verification, in one
fresh zsh process:

```sh
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP
setup_spack
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/thisdd4hep.sh
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/geant4.sh
cmake -S prototypes/short_strip_redesign -B build/short-strip-redesign/native-final -DBUILD_TESTING=ON
cmake --build build/short-strip-redesign/native-final -j4
ctest --test-dir build/short-strip-redesign/native-final --output-on-failure
python3 -B tools/short_strip_redesign/curate_native.py --input build/short-strip-redesign/native-final/native.json --output docs/validation/DES-043/native-summary.json
```

Default construction is the first mirrored pair,792sensors, including every
ring, phi seam and staggering pattern. `-DNODD_RED_FULL=ON` in a separate build
directory constructs all12discs/4752sensors; this option is a recipe, not a claim
that the full native mode has run. Source coverage evaluates all6station datums.
Only the explicit module/petal/local services are constructed; shared barrel/
endcap trunks and full-tracker integration are not duplicated into this model.

`native-summary.json` is an aggregate report, with producer/configuration/input/
compact/material/library hashes and actualROOT/runtime versions. Full generated
XML, expected-entity maps, build products and rawROOT/logs remain ignored under
build/. Composite windows and intersecting tube cuts intentionally defeat the
old sum-of-cut-volume approximation: this native check asserts no exact mass.
The separate changed-component material ledger remains a scoped upper allowance.

The native checker verifies every named solid's centre/material/CSG presence,
sensor sizes/frames/IDs and75umx2mm cell centres; opens backing/cold windows;
brackets each actual graphite/Ti pipe interface with two-sidedContains probes;
and runs ROOT overlaps at1e-5mm. Missing contacts hard-fail even with zero
overlap counts. Tube contact does not measure the required thermal resistance.

## Complete thermal stack and barrel source evidence

The old−22.163°C downstream estimate omitted a named50umASIC bond and an
upstream leakage path. IndependentPhysVal06 identifies this omission. The final
screen retains0.04K/W other-interface allowance, adds the bond atκ≥1.2W/m/K
(R≤0.03804758K/W over two complete23.4mmtiles), and budgets an additional
upstream sensor/bump/redistribution≤0.5K/W (1K at2W). This last value is an
unverified requirement, not a derived feasible resistance. Correctednominal/
adverse/stress values are−23.812/−20.333/−13.374°C. Adversemargin0.333K is tight;
qualifiedcoldcontacts, bondedarea, irradiation, leakagefeedback andFEA remain
required. Geometrycontact alone does not certify temperature or thermalrunaway.

The [barrel source screen](barrel-summary.json) and
[recipe](../../../tools/short_strip_redesign/barrel_interfaces.py) check the
proposed20x64mmlands at±12mm, allsame-layer stavepositions with conservativerow/
radialexclusions, module/support/bus/footOBBs, tubecontact andwindowedge lands.
The repeatable calculation makes3170144boxcomparisons withzerointersections;
newCu-rail separation bound1.285266mm, bearing-ring clearance7.707659mm and
minimum straightpipecontact58.666667mm. These are sourcebounds, not native
barrelCSG or thermalqualification. Default476-source pins can be overridden
with `--source-revision COMMIT` while all oldsourcehashguards remain enforced.

```sh
python3 -B tools/short_strip_redesign/barrel_interfaces.py --source-revision HEAD --output build/short-strip-redesign/barrel-interfaces.json
```

The source and input hashes in the committed report identify its exact execution.
No reference-run payload, event file, generatedXML orROOT geometry is committed.

## Final executed evidence

Final native execution and generation both identify
`d21880cc90ce275abeab624c009eea7e4eca76db`. Actual reportSHA256:
`234f904026f305f3e404ec4e9a53609752e37069b78611466472a802112c0d1b`.
The direct validator returnedPASS with792actualsensors/uniqueIDs,3960cellchecks,
16132solids/1656CSG,7200contact/windowprobes,zerooverlaps/extrusions at1e-5mm,
andzero missingcontacts. Engineering status remainsUNQUALIFIED. ROOT6.40.04,
Python3.14.5; pointfilling193.377s andoverlapcheck0.601s. No user randomseed was
supplied toROOT's default checker; source-model/ray screens are deterministic.

The actual direct command after the verified environment/build was:

```sh
python3 -B tools/short_strip_redesign/validate_native.py --compact build/short-strip-redesign/native-final/compact/short-strip-redesign.xml --expected build/short-strip-redesign/native-final/compact/expected.json --library build/short-strip-redesign/native-final/libnODDShortStripRedesign.dylib --output build/short-strip-redesign/native-final/thermal-complete-native.json
```

The nativeCtestcommand above is a reproduction entrypoint; this retained final
result comes from the direct command. Source/input/validator hashes were checked
before and after execution. Generatedgeometry/materials remainedbyte-identical
to the separately preserved476nativePASS snapshot. The changed thermal model
was not used to relabel the earlier report.

Final20portabletests, complete numerical replay and10PNG/PDFfingerprints pass.
All10figure files were regenerated independently and matched byte-for-byte.
The aggregate native evidence and barrel source report are also source-hash
checked by `verify.py`. The CI runs source controls/replay/barrel checks;
this does not imply hosted CI has executed the node-specific native job.

Independentassessment history and limitations are in the
[session reconciliation](../../../logs/codex/SESSION-2026-11-02-short-strip-service-redesign/assessments.md).


## Combined working-baseline update — 2026-11-03

The human subsequently requested integration into the current DD4hep tracker, the actual ODD TDR and merge preparation. See the separately dated [combined integration record](integration/README.md), [independent fixed-revision assessment](integration/assessment.md) and [publication receipt](../../publication/short-strip-services-2026-11-03/README.md). Those records supersede the earlier pending-integration wording above without changing the standalone November 2 evidence or its provenance.
