# DES037 — Barrel HCAL design evidence

2026-10-15. **DRAFT / PROTOTYPE.** Analytical assembly design using the
human-directed DES036 working module. No production or engineering acceptance.

## Exact execution and retained artifacts

Executed model/config/design source at
`c83e6f4eaebdaa354217b79b963df15c6c3c0a96`. The working checkout was dirty
with then-untracked drawings, records and evidence; model/config/design bytes
matched that commit. [summary.json](summary.json) records exact source hashes,
the unchanged unit/material ledger, per-layer counts/phases, constituent masses,
conditional power/data budgets and hashes of complete exports. The full
54,912-carrier layout and per-phi masks remain in ignored `build/hcal-barrel`.
[coverage.json](coverage.json) retains statistics and explicit seam probes,
identifies the full output hash and labels the omitted raw count matrix.

The [drawing inputs](../../design/figures/DES-037/inputs.json) bind the actual
summary/mask/context bytes and drawing producer. The generated PNG was visually
inspected. The new regional R–Z panel is a proposal overlay; the selected
LAYOUT001 JSON and its existing R–Z image are unchanged.

## Checks actually run

| Check | Observed result |
| --- | --- |
| Regional geometry/ownership/fault controls | **15 passed**, exit 0 |
| Whole-carrier analytic containment | Every placement checked at all eight corners against narrow sector face and end-flange bounds |
| Placement/ID/frame consistency | 54,912 unique parent IDs, declared row/column/grid agreement, proper orthonormal sector frames |
| Material accounting | Common unit excludes reference absorber; steel, rails, cover and flange domains are disjoint; constituent totals conserve the partial ledger |
| Directional core planes | 61 signed eta samples × 720 uniform phi probes × 3 scenarios = **131,760** sampled counts, plus 64 separate exact boundary probes |
| Steel-only paths | Analytic IP clipping per steel layer, including sector and axial limits; central normal control is 1,080 mm |
| Independent PhysVal | 15 regional controls passed; **3,105** global tile-centre/near-edge probes had zero lookup discrepancies |
| Independent SysArch | Source/domain/frame assessment and transform checks; no blocking defect in the bounded analytical scope |
| Drawing | SVG/PNG rendered from actual exports and inspected; line-end whitespace normalized |

The common-module and historical calorimeter regressions are recorded in the
session closeout after their actual executions. Standard-library controls do
not prove native construction or detector acceptance. Source/figure/link checks,
project/session validators and the local token-site build are separate repository
checks, also retained in the journal.

## Partial inventory and geometric consequences

| Quantity | Result |
| --- | ---: |
| Paired carriers / common boards | 54,912 / 109,824 |
| Physical tiles / powered internal channels | 3,953,664 / 8,566,272 |
| Unused ordinary / auxiliary channels | 3,953,664 / 658,944 |
| Common local hardware mass | 165.720 t |
| Steel + named support/cover mass | 1,605.142 t |
| Total modeled mass | **1,770.862 t** |
| Nominal local heat / ideal water at 5 K rise | **326.143 kW / 15.605 kg/s** |
| 100 µA / 1 mA per-device current stress heat | 342.417 / 491.865 kW |
| Four cooling handoffs per carrier | 219,648 endpoints |
| Complete-face projected core fraction | **39.51–59.30%**, varying by layer |

There is no uncertainty distribution or certified plant requirement. Bias
regulation, additional external conversion/concentration, collectors/cables,
mounts, bearings and lifting/handling hardware are excluded. The summed local
12 V input current, approximately 27.15 kA, is a distribution warning rather
than a proposed regional feed. The 750 kHz/1 MHz scenarios retain **93.75% / 125%**
local chip DAQ utilization. Trigger capacity is separate. Summing lanes does not
qualify a carrier or sector concentrator, framing, FIFO queues or sustained rate.

Selected core-plane statistics use only the 720 uniform phi probes; explicit
sector-boundary controls do not reweight those statistics:

| eta | Sampled min / mean / max planes | Zero-plane fraction |
| ---: | ---: | ---: |
| 0 | 0 / 27.467 / 36 | 4.44% |
| 1.0 | 0 / 12.956 / 18 | 4.44% |
| 1.2 | 0 / 2.089 / 3 | 15.56% |
| 1.3 | 0 / 0 / 0 | 100% |

The adverse +130 mm aligned control gives zero at the midplane across sampled
phi. A phase-zero aligned control already includes a central active row and is
retained separately. All controls have identical carrier/layer counts and area;
actual tangential shifts are explicitly reduced near a column-count transition
or outer edge. Staggering improves some paths and cannot remove fixed sector
cracks. Signed-eta scans are retained rather than assuming the asymmetric common
carrier service bay gives exact barrel reflection symmetry.

These are actual physical core **planes at local z = 2 mm**, ahead of the rear
recess; they are not complete finite-solid tile/recess intersections, efficiency,
optical response or shower sampling predictions. Steel-only path length omits
other material and is not a total X0/lambdaI/containment result. Exact seams may
miss steel as well as cores. No interpolation fills those gaps.

## Reproduction

Actual design/control runtime: system Python **3.14.6**, standard library.
Drawing: existing Python/Matplotlib **3.11.2** in the preinstalled ACTS virtual
environment, with writable temporary font caches. No dependency installation or
new DD4hep/Geant4 activation was needed or performed.

```sh
python3 -B -m unittest discover -s tools/hcal_barrel -p 'test_*.py' -v
python3 -B tools/hcal_barrel/design.py --output build/hcal-barrel
python3 -B tools/hcal_barrel/draw.py --directory build/hcal-barrel --output docs/design/figures/DES-037
```

The drawing command needs an existing Matplotlib environment. Source/config and
complete output hashes identify the executed instance. Later revision metadata
changes when regenerating at a later Git commit; geometry is determined by the
recorded inputs. [Tool guide](../../../tools/hcal_barrel/README.md).

## Review limits and next design gates

[Independent review](review.md) closed the earlier matched-count phase issue.
Residual sector-edge gaps are **not suitable for claiming detector acceptance**.
Compare intact common-board edge carriers or a revised carrier hierarchy before
freezing full sampling requirements. Reconcile the +62.1 mm envelope amendment,
ECAL rear egress, combined barrel/endcap material depth, supports and muon/magnet
interfaces. The overlap of outline ray intersections is not a containment proof.

Full-assembly native overlaps/material paths/IDs, finite-solid navigation,
connected collection and frame penetrations, regional power/DAQ topology,
thermal/hydraulic/structural studies, radiation/occupancy/EOL inputs and
shower/digitization/leakage validation remain **NOT RUN**. Inherited DES036
native/saved-hit checks support only the common unit. Only humans may grant
engineering approval, production integration or detector acceptance.
