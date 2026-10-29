# Selected balanced tracker baseline — 2026-10-29

The expert-selected **balanced** configuration is the maintained working
simulation baseline. [The decision record](../../design/inputs/DES-040-balanced-selection.json)
retains noemina's APPROVED review5701456683 at
`cfd15cb1c0a195a73a8204400b115a2635a52e2a` and the maintainer's explicit
implementation direction. It does not assign engineering sign-off or ACCEPTED
status to DES040. The numerical study and its adverse results remain retained.

## Maintained geometry

The default barrel, combined pixel and full tracker exporters use the central
balanced placement contract. Barrel radii are31.5/57/96/182mm with12/22/18/30
staves. Existing endcap logical IDs1–9 move to |z|615/865/1115/1333/1565/1780/
2090/2440/3070mm. Added ID10 repeats original donor2 at |z|950mm, on both ends.
Original local module/support/cooling geometry is generated at the donor datum
and rigidly relocated; it is not repacked at the new z. Collectors follow their
discs and carrier slots follow the ten physical stations. Envelopes, module
types, strips and pipe stay fixed. Historical explicit configs remain controls.

There are5,666 pixel modules/12,410 sensitive patches, including2,616 endcap
modules/5,616 patches and280 endcap cooling circuits. The tracker has46,250
planes in54 signed logical groups. The standalone pixel model mass is204.747kg;
the integrated tracker clips passive apertures to28.8mm outside the27.8mm pipe.
Global pixel trunk/bypass/rear material inventories remain frozen reference
allocations. Their cumulative connectivity/capacity and engineering margins
remain unqualified.

## Actual execution

Generator source: `888069bb7c0ec04760ff8ea2288316b6cbf86835`.
Canonical integrated compact SHA256:
`81e2d439a66f0978d0613929842cf6aa4658cd0e0300ede7513d30caae296023`.
The native audit records the working-tree dirty flag and exact execution hashes;
the TDR extraction independently confirms that all its producer fingerprints
match committed888069b bytes. Documentation edits are not substituted for
native execution identities.
The Gen3 entry point ran as a new uncommitted wrapper at that generator HEAD;
its exact executed file fingerprint was subsequently committed in ccdafc8. Its
file/binary fingerprints, rather than HEAD alone, identify the conversion code.

| Check | Observed result |
| --- | --- |
| Fresh CMake/Ninja DD4hep build | Five factory libraries and all canonical exports built |
| Full native ROOT audit | PASS;687,724 placements;zero overlaps/extrusions at1e-5mm |
| Sensitive identities/frames |46,250 unique VolumeIDs;maximum centre residual5.22e-13mm |
| Exclusive material inventory |1,168 materials matched;minimum passive pipe clearance1mm |
| Gen3 source comparison |46,250 unique geometryIDs;54groups;120volumes;all source frames matched |
| Complete native Gen3 JSON round trip | Identical decoded/re-encoded payload |
| Geant4 construction/transport | Three1GeV geantino events, seed62042003, FTFP_BERT, direction(1,0,1);three ROOT events written |
| Maintained/source study equivalence |103,460 local nodes matched by the retained diagnostic; independent SysArch/PhysVal assessments additionally cover materials, global attachments and all strip/pipe trees |

The verified installed runtime is DD4hep1.38, ROOT6.40.04, Geant411.4.3 and
native Python3.14.5. Spack setup/lock fingerprints changed since the old study;
imports and all12 Geant4 datasets were checked directly. No shared installation
was changed. Binary hashes identify the ACTS runtime; current external source
HEAD is not asserted to be its compiled revision. Full external source access
was not established by this execution.

[Native audit](native-tracker.json.gz), [Gen3 source audit](gen3-source-comparison.json.gz),
[Gen3 native frames](gen3-native-report.json.gz), [finite portals/frames](gen3-geometry.json.gz),
[Geant4 smoke](geant4-smoke.json), [local-node diagnostic](canonical-source-equivalence.json)
and [source/evidence fingerprints](manifest.json) retain the results.

## Reproduction

In a fresh verified ACTS Spack shell, use the existing
`software/env/truth_tracking.sh` runtime without modifying shared dependencies:

```sh
cmake -S . -B build/balanced-baseline/dd4hep -G Ninja -DBUILD_TESTING=ON
cmake --build build/balanced-baseline/dd4hep --parallel 8
python -B tools/tracker_dd4hep/validate.py \
  --compact build/balanced-baseline/dd4hep/detector/tracker/tracker.xml \
  --expected build/balanced-baseline/dd4hep/detector/tracker/expected.json \
  --library-dir build/balanced-baseline/dd4hep/detector \
  --output build/balanced-baseline/native-tracker.json
python -B tools/tracker_dd4hep/export_gen3.py \
  --build-dir build/balanced-baseline/dd4hep \
  --output-dir build/balanced-baseline/gen3
python3 -B tools/tracker_dd4hep/verify_baseline.py
python3 -B docs/publication/tracker-baseline-2026-10-29/scripts/balanced_snapshot.py --check
```

Fingerprint verification replays provenance checks; it does not rerun native
construction or transport. DDSim additionally needs the local factory directory
in DD4HEP_LIBRARY_PATH and DYLD_LIBRARY_PATH on macOS, and invocation through the
active Python. The first smoke attempt lacked that path; the corrected run
passed. The historical material-survey exporter rejected the new inventory by
its original fixed-count guard; it remains unchanged, with a separate current
baseline entry point above.

## TDR and remaining limits

The [current full-tracker review edition](../../publication/tracker-baseline-2026-10-29/README.md)
imports the exact existing TDR source7625cf6054f5761228be6d8d2de24d43f155bd19.
The pixel chapter, station/population tables and six geometry-dependent figures
are updated. Strip chapters, six strip figures and their table are unchanged.
This repository-owned review artifact does not publish to Overleaf or change
the external TDR submodule. Source/figure checks and pdfLaTeX CI are separate
from compiled-page visual review. The built-in Tectonic engine cannot compile
the existing pdfLaTeX-specific house style; the repository's pdfLaTeX workflow
compiled the manuscript successfully.

The approved performance remains the retained Fatras truth-tracking study,
using constant3T, geometric digitization and Gaussian cross-checks. Its existing
material profiles are relocated and its added disc uses homogeneous downstream
material. Detailed DD4hep donor assemblies do not establish a fresh Geant4 map
or new response validation. The1GeV momentum regression, forward d0 limitations,
residual tails and incomplete uniform ten-hit coverage remain explicit accepted
tradeoffs in the selected working baseline.


Independent PhysVal comparison joins physical sensors by their five readout-ID
fields. All46,250 centres, signed axes and bounds correspond (maximum floating
difference1.14e-13);120volumes,124portals,250link subsurfaces and54logical groups
correspond. Exactly602ACTS sensitive IDs are permuted within added logicalID10
because source-path label ordering changed. Existing layers retain their IDs.
All checked per-physical-sensor digitization payloads remain equivalent, as do
54geometric/54pooled calibration groups and67material keys/68roles/8552bins.
The homogeneous added-disc material lies1mm after the farthest sensor face.
This establishes compatibility for the checked study payloads, not universal
sensor-ID byte identity or compatibility with arbitrary per-sensor payloads.


The final corrected full report is32pages. [The PDF](balanced-tracker-tdr.pdf),
[compiler log](balanced-tracker-tdr.log.gz) and [compile/page-review record](pdf-review.json)
are retained. pdfLaTeX CI40937879945 passed atb19a12b; the source-tree and asset
manifest fingerprints identify the compiled manuscript. All32pages were rendered
and visually inspected, including detailed pixel tables, figures and the
standalone/integrated qualification. The compiler reported no overfull boxes or
unresolved references/citations.

Separate PhysVal review also inspected all32pages and every pixel/overview page individually, verified the PDF hash and reported no remaining blocker in its assigned scope. [Bounded technical assessments](technical-assessments.json) retain the exact source and limits.
