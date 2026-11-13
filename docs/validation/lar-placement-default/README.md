# Reusable LAr periods in the maintained LAYOUT-002 export

The maintained tracker/ECAL exporter selects solid inclined-period mothers for
the ALLEGRO-style LAr barrel and turbine endcaps. One barrel template is placed
1536 times; three turbine templates are placed 384/720/1360 times on each end.
The user's 2026-11-13 instruction authorizes this software default for the
DRAFT / PROTOTYPE candidate. DES032/DES033 design sign-off remains open.

The [placement investigation](../lar-placement/README.md) retains the exact
geometry/readout comparisons and one matched serial timing pair: 522.258406 s
versus 67.382542 s to the first event, including the fixed audit/setup workload.
This follow-up verifies the maintained export route. It does not repeat that
comparison or establish a general response or multithreading result.

Standalone component exporters retain their legacy assembly defaults for
reproduction. Pass `--real-periods` there to obtain the maintained hierarchy.
Existing dimensions, material recipes, placements and readout encodings remain
the same. The R–Z drawing inputs therefore retain their physical bounds.

## Validation

Executed results and exact artifact bindings are recorded in [results.json](results.json).
Full generated XML, logs, ROOT files and leaf inventories remain under ignored
`build/lar-default/`. Source revisions, installed library artifacts and executed
configuration hashes are recorded separately.

A fresh maintained export restores the complete legacy tracker/ECAL XML after
removing only the four new envelope declarations. Material definitions are
byte-identical. Both ECAL detector subtrees also match the measured candidate:
the comparison normalizes only the envelope declaration's sibling position
(the variant helper appends it; the standalone exporter emits it first) and
indentation. All other XML attributes, ordering and text values are compared.
The [comparison helper](check_export.py) records its inputs and source hashes.

The fresh ECAL-only probe retains all 43,648 sensitive IDs and 274,689 terminal
material leaves, with inventories byte-identical to the investigation candidate.
The native DD4hep and Geant4 sensitive transforms agree within the retained
1e-7 mm centre and 1e-10 axis tolerances. All seven saved events pass primary,
finite-hit, canonical-ID and aimed barrel/wheel/side checks. No timing ratio is
derived from this follow-up run, which overlapped the native scan.

## Reproduce

Use the reverified existing Spack runtime through `software/env/run.sh`.
No new package installation is required. Build the existing tracker factories
as in the [baseline recipe](../../../tools/calorimeter_baselines/README.md#native-union-check).
The LAr factories are those from PR138; rebuild them if the recorded artifacts
are unavailable.

```sh
python3 -B tools/calorimeter_baselines/export.py --layout LAYOUT-002 --output build/lar-default/layout002
python3 -B -m unittest discover -s tools/calorimeter_baselines -p 'test_*.py' -v
python3 -B -m unittest discover -s tools/lar_calorimeter -p 'test*.py' -v
```

To repeat the XML comparison, set `legacy_compact` to the full maintained export
at the investigation revision (legacy default) and `candidate_compact` to its
measured ECAL-only candidate. The prior report records their generation recipes;
the exact retained input hashes are in this report's results.

```sh
python3 -B docs/validation/lar-placement-default/check_export.py \
  --baseline build/lar-default/layout002/detector.xml \
  --legacy "$legacy_compact" --candidate "$candidate_compact" \
  --output build/lar-default/xml-comparison.json
```

Run `tools/calorimeter_baselines/native.py` on that directory with all five
tracker and both LAr libraries. It constructs the complete maintained
tracker/ECAL union and scans overlaps at 10 nm. Then run the existing
`tools/lar_calorimeter/placement_probe.py --smoke` on its `detector.xml`, with
both LAr libraries and a fresh output directory, followed by
`placement_smoke.py`. The latter probe extracts the complete ECAL components;
its seven saved electrons cover the barrel and each wheel on both ends at
B=0, 20 GeV, FTFP_BERT, 0.7 mm cuts and one worker. It does not transport the
tracker or exercise a 12-worker campaign. See the investigation recipe for
the fixed directions, seeds and native/readout audit definitions.
