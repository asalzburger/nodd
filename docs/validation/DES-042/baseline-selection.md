# Selected strixel working baseline — PR109

Human **asalzburger-review** selected 2 mm on 2026-11-02 and approved PR109 at
its study head `07b38a7814853ec2e44ef9102098c908f45a2147`.
[Selection comment](https://github.com/asalzburger/nodd/pull/109#issuecomment-6573426341) ·
[Approval](https://github.com/asalzburger/nodd/pull/109#pullrequestreview-5734614248) ·
[Decision and parameters](../../design/inputs/DES-042-strixel-selection.json).
This records the observed human working-baseline decision; DES042 remains DRAFT.

| Selected quantity | Value |
| --- | ---: |
| Fine × local-v pitch | 75 µm × 2 mm |
| Ideal binary σu / σv, pitch/√12 | 21.65 / 577.35 µm |
| Channels per 48 × 96 mm² active sensor | 640 × 48 = 30,720 |
| Barrel: 8,064 sensors | 247,726,080 |
| Both endcaps: 4,320 sensors | 132,710,400 |
| Total strixel channels | 380,436,480 |

The channel count is one quarter of the previous 0.5 mm value. Binary resolutions
are ideal single-cell inferences, not calibrated hit or reconstructed-track errors.
Local-v is longitudinal z in the barrel and radial in the endcaps.

The [100-event ttbar comparison](ttbar-pu200/README.md) reports guide-selected
hard-scatter efficiency80.3627% at both0.5/2mm; the paired difference has95% interval
[−0.210904,+0.201545]percentage points. Fake fraction rises0.195437→0.229765%,
with difference+0.034329[+0.005459,+0.063788]percentage points. Equal aggregate
efficiency is not equivalence. The unchanged graph edge cap is reached99/100events.
Gaussian response, boundary retry coupling, constant3T, fixedmaterial andqqbar-only
hard-process qualifications remain. The [single-particle comparison](gbts/summary.md)
shows some longitudinal resolution degradation.

## Reproduce the selected readout

The maintained assembly configuration links the decision. Export from a fresh
output directory; output is local and must not be added to the PR:

```sh
python3 -B tools/tracker_dd4hep/export.py --output build/strixel-2mm-source
python3 -B -m unittest discover -s tools/tracker_dd4hep -p 'test_*.py' -v
```

Both strixel readouts in `tracker.xml` use grid(0.075,2)mm and offsets(0.0375,1)mm.
The assembly report records old/new segmentation and selection SHA256. Historical
standalone component exports still use0.5mm and their original source pins.
The assembly override changes no physical volume, material, sensor placement or ID.
The retained DES040 native checks/TDR are explicitly dated controls; their three
amended source files are verified at the reviewed pre-selection revision against
the unchanged manifest. Current selected readouts have separate regression gates.
No new native DD4hep/Geant4 or ACTS execution is claimed by this source export.

## Prepare the selected Gaussian surrogate

Use the fresh native sensor report from the selected assembly and a0.5mm error
table remapped by physical roles to those same native volume IDs. If IDs changed,
first use the existing `tracker_optimization/material.py` physical-role remapping;
do not transplant pooled volume IDs. Explicitly identify the reference pitch:

```sh
python3 -B software/analysis/tracker_baseline/prepare_response.py \
  --native-report build/strixel-2mm-native/native-report.json \
  --baseline-error-table build/strixel-2mm-native/remapped-0p5mm-errors.json \
  --reference-pitch-mm 0.5 --output build/strixel-2mm-response
python3 -B -m unittest discover -s software/analysis/tracker_baseline -p 'test_*.py' -v
```

This pure JSON step reuses the studied response prescription: only systems4/5,
coordinate1 sigma scales×4; variance therefore scales×16. Pixel, strixel fine
and one-coordinate long-strip errors remain unchanged. Merging is disabled.
The report fingerprints inputs/helpers; no native import or shared installation
is required. This is a surrogate extrapolated from0.5mm widths, not independent
2mm calibration or a new reconstruction campaign. The frozen PR107 runner still
requires its historical compact; its guard is retained. For native benchmarking,
use the [DES042 runner](../../../software/analysis/strixel_reconstruction/README.md)
and explicit `*-pitch2` cases; ttbar uses the corresponding pitch2 case in its
[repeat recipe](../../../software/analysis/strixel_ttbar/README.md).

The dated October29 TDR and all study comparisons are historical source editions.
This addendum is the current readout amendment. R–Z drawings retain valid physical
bounds. ASIC footprints, cables, cooling and passive material are unchanged;
conditional power/cable savings require a separately qualified hardware redesign.
Full run payloads remain local; retain plots, compact summaries and recipes only.
