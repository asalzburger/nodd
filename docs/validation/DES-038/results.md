# DES038 — Endcap HCAL design evidence

2026-10-15. **DRAFT / PROTOTYPE.** Analytical regional proposal using the
human-directed common module; no production or engineering acceptance.

## Exact execution and retained artifacts

Executed model/config/design source at
`7c7f0ba96b69dd754d6e25bd97cef4cfe502bcae`. Dirty state records the ongoing
drawings, session and evidence work; model/config/design bytes matched that
commit. [summary.json](summary.json) identifies source/config/common-module and
complete output hashes. [coverage.json](coverage.json) retains every statistic
row, proper negative-end mirror checks and explicitly unrun steel-path scope.
The 33,984-placement layout, physical unit template, all transformed service
endpoints and 92,160-ray CSV stay in ignored `build/hcal-endcap`.

[Drawing inputs](../../design/figures/DES-038/inputs.json) bind actual export and
context bytes plus the producer. The PNG was visually inspected. Its R–Z panel
shows the regional proposal against the existing outline; selected LAYOUT001
JSON/image geometry is unchanged pending review.

## Checks actually run

| Check | Observed result |
| --- | --- |
| Regional controls | **19 passed**, exit 0 |
| Whole-carrier fit | Exact convex aperture separation and outer-corner containment for every pattern/phase; no clipped hardware |
| Placement/ID/ownership checks | Complete two-end placement inventory, unique IDs, local grid and source consistency, no repeated reference absorber |
| Proper negative-end rotation | Origin, basis and port positions/directions use Rx(pi); sampled masks match under `(eta,phi) → (−eta,−phi)` |
| Physical plane masks | **92,160** sampled counts: 32 eta values × 720 phi probes × 4 controls |
| Independent PhysVal | 19 controls passed; **3,105** independent global centre/near-edge probes, zero lookup discrepancies |
| Independent SysArch | Shape/material/interface/frame assessment, with the unconnected-reservation caveat below |
| Steel ray/material paths | **NOT RUN**; no finite-depth endcap steel-path result implied |
| Drawing | Actual full-face/inner-packing/R–Z/mask figures rendered and inspected |

The common-module and historical calorimeter regressions, source/link/hash and
repository record/site checks are recorded in the session after execution.
Native whole-endcap construction/transport is not inferred from these tests or
the historical common-unit smoke.

## Inventory, packing comparison and sampling limits

| Quantity | Result |
| --- | ---: |
| Uniform / aperture-adaptive pairs per layer per end | 468 / **472** |
| Adaptive-grid angular-boundary filter | 304 pairs per layer per end |
| First projected core radius, uniform / adaptive | 418.099 / **328.598 mm** |
| Full-face / packable-face core fraction | **55.0308% / 55.5882%** |
| Both ends: paired carriers / boards | 33,984 / 67,968 |
| Tiles / powered internal channels | 2,446,848 / 5,301,504 |
| Total partial modeled mass | **1,019.273 t** |
| Common hardware / steel / annular frames / back covers | 102.561 / 909.204 / 4.566 / 2.942 t |
| Nominal local heat / ideal water at 5 K rise | **201.844 kW / 9.658 kg/s** |
| 100 µA / 1 mA per-device current stress heat | 211.915 / 304.406 kW |
| Local coolant endpoints | 135,936 |

The filtered grid is a controlled cost-of-boundary diagnostic, not an optimized
wedge layout. Adaptive rows repair the uniform origin without a custom board.
The rotated and aligned adaptive patterns have equal counts/area/material/heat;
their directional samples differ. The full-face denominator includes frame and
joint/packing losses; the packable denominator excludes only the annular frames.
No area is discarded to manufacture a coverage gain.

Selected active-plane results at 720 uniform phi probes:

| Eta magnitude | Sampled min / mean / max | Zero-plane fraction |
| ---: | ---: | ---: |
| 1.2 | 9 / 15.769 / 21 | 0% |
| 2.0 | 13 / 21.728 / 29 | 0% |
| 3.0 | 9 / 21.108 / 33 | 0% |
| 3.5 | 0 / 3.633 / 13 | 33.33% |
| 3.8, 4.0, 5.0 | 0 / 0 / 0 | 100% |

These are core-plane samples at local z = 2 mm, ahead of the recess. They do not
measure finite-solid crossings, optical response, efficiency or containment.
Staggering improves sampled minima but does not make all rays fully sampled.
At eta4 even the proposed rear radius along an IP ray is only 236.029 mm,
inside the unchanged aperture. The existing FCal reservation is unchanged and
empty; its presence does not close forward coverage or hadronic shower depth.

The common current/latency/DAQ assumptions remain conditional: chip DAQ
utilization is 93.75% at 750 kHz and **125%, OVERLOAD** at 1 MHz. Trigger lanes
stay separate. Summed local 12 V inputs, lane budgets and ideal coolant flows
are not a certified plant/voltage/concentrator design. External collector/cable
material, regulation/concentration losses, fasteners, bearings and mounts are
excluded. Stress currents are not predicted irradiated end-of-life behavior.

## Unconnected service and mechanical interfaces

The source explicitly marks collector handoffs `connected=False` and records
empty row/column reservations. Endpoint transforms are checked; endpoint routing
is not. Annular frames contain material and need actual crossing ports. In
negative-y quadrants the unchanged +y connector bay does not automatically face
the generated outward row strip. Aperture-adjacent ports can meet the inner-frame
boundary. Do **not** interpret every reservation/handoff label as an installed
or geometrically completed connection. This is an exposed design gate, consistent
with the source scope and [SysArch review](review.md).

Steel plates exclude quarter joints and annular frames. Empty local row/column
service strips do not remove absorber. The partial ledger owns each frame/cover
once. Load transfer, rotated-layer assembly/access, ring/plate attachments and
handling remain unqualified; transport material is not structural or B–H data.

## Reproduction and remaining gates

Executed with system Python **3.14.6**, standard library. Drawing used already
installed Matplotlib **3.11.2** in the existing ACTS virtual environment with
writable temporary font caches. No dependency installation or fresh DD4hep /
Geant4 runtime operation was performed.

```sh
python3 -B -m unittest discover -s tools/hcal_endcap -p 'test_*.py' -v
python3 -B tools/hcal_endcap/design.py --output build/hcal-endcap
python3 -B tools/hcal_endcap/draw.py --directory build/hcal-endcap --output docs/design/figures/DES-038
```

The last command needs an existing Matplotlib environment. Complete exports are
hashed rather than committed as large files. Regenerating at another revision
changes Git execution metadata; the recorded configuration drives geometry.
[Tool guide](../../../tools/hcal_endcap/README.md).

[Independent review](review.md) found no new scoped code/claim defect after the
source/origin follow-up. The proposal still needs a reviewed forward and
barrel/endcap handover, residual inner/edge sampling requirements, connected
collection/frame ports and regional power/readout architecture. Full native
construction/material paths, finite-solid tile/recess and steel navigation,
thermal/hydraulic/structural work, regional radiation/occupancy/EOL assumptions,
shower/digitization/leakage checks remain **NOT RUN**. Human engineering approval
and detector acceptance are pending.
