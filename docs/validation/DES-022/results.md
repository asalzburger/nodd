# DES-022 — actual prototype results (2026-10-07)

DRAFT, isolated PROTOTYPE; no production integration or sign-off.
Native DD4hep1.38 / ROOT6.40.04 / Geant4 11.4.2; actual dirty execution starts
at a9d6367bbe750f72545e933e620c0b53673da83c. Exact source, input, compact,
material, plugin and retained artifact hashes are in the receipts and native
report. Enclosing result commits are not execution hashes.

The cooled5 mm core and0.2 mm skins are the stave, with two truly1D strip sensors
per module (1200 strips/face, ±20 mrad stereo). There are86/108 staves,36 pairs
per stave:6984 pairs/13968 sensors, versus3151 pairs in the frozen DES-011 barrel.
The increase buys overlap for finite stereo separation and curved incidence;
it is a substantial silicon/channel/material cost, not a free coverage gain.
Sensor mid-plane separations6.7/9.7 mm replace the unbuildable5 mm analytical gap.

## Structural recommendation

Minimum under the declared released-span screen: **15 stations**.
14 stations give42.25 µm,
above the40 µm gravity allocation. Recommend **17 stations/stave**,
spacing163.75 mm, at the exact coordinates in the
inventory. Full attached load is1.8004 kg per worst
stave; only grounded bearing rings are excluded. At E70 GPa, core G5 MPa and
2× gravity: bending5.06 µm,
core shear20.67 µm,
total with overhang allowance25.95 µm.
The independent continuous Timoshenko mesh gives
23.46 µm;10/20 mm refinement
agrees within0.1 µm. Reserve a further10 µm for the support/joint compliance.
No skin/foam modulus or bond/bolt/torsional response has been measured here.

The web is on the free shingle edge, buses/hybrids on the opposite edge.
Two potted epoxy/Ti lands tie each station to its keyed CFRP web and a tangent
CFRP bearing ring. One central station fixes z; the others slide longitudinally.
Specify ±0.3 mm longitudinal slot travel as an unsigned assembly provision:
CTE2 µm/m/K,50 K and1.31 m give0.131 mm thermal motion, plus0.1 mm assembly
allowance. Slots/clamp geometry remains an effective nominal fixture; joint,
ring and global frame FEA, thermal bow, vibration, indentation, fatigue and
installation preload must close before qualification.

## Routing and electrical/thermal limits

Each half-stave has two U circuits, nine complete pairs/circuit. Four straight
pipe legs and separated10 mm centre-radius return bends are explicit, with
contained/disjoint foam holes. Both faces connect to insulated buses and end
boards; two12-pair harnesses per half-stave count complete pairs once.6 mm Cu/HV
bundle and3.6 mm/48-fibre bundle are conductor/volume hypotheses. Reference
LV loop/return drops0.397/0.199 V pass;1.4× warm resistivity fails the return
screen. This requires electrical and dielectric qualification, not a claim
of a manufactured cable.

Barrel-only reference and adverse packing pass the unchanged r1144–1169 mm
corridor for the conductor-sized proposal. The13.4 mm power-bundle benchmark
fails even reference packing. Combined endcap services are a separate DES-023
screen. Collector occupies z1325–1435 mm; the old long-disc datum1403.65 mm is
incompatible. DES-023 must propose a new first datum and preserve its losses.
R50/R25 cable/pipe bends are reservations; fitting/connector CAD, weld access,
CO2 pressure drop, flow stability and supply/return distribution are unqualified.
Thermal numbers are lower-bound slabs with unsigned foam conductivity;
interfaces, lateral spreading, irradiation/leakage and warm coolant need proof.

## Actual validation

Eight model/negative controls passed (source drift, tube/core rejection,
material overfill rejection, stereo pair geometry, shear dependence, point load,
closed-form uniform load and independent continuous-beam limit).
Native construction/role counts/positions/signed axes/solids/mass/true1D strip IDs:
PASS, **zero overlaps at1e-5 mm**,105 ROOT navigation/material rays.
Fresh ROOT process:13968 sensors and exact constituent inventories/axes persisted.
DDSim zero-field10GeV transverse muon, seed42, FTFP_BERT: eight saved
positive-energy hits, same-module pairs in both layers. It tests transport,
not physics performance or continuous coverage. No ACTS conversion was run.

Vacuum coverage:77760 tracks (eta−4..4 step0.1,64 off-grid phi bins, luminous
z−150/0/+150, B0/4 T, pT1/10GeV, both signs); fast finite planes agree with the
independent oracle on164 tracks including off-axis vertices. Fixed old ideal
cylinders and an immutable old/new finite-plane subset are retained. Remaining
misses by [layer0,layer1]:

- B0 T, pT1 GeV, q1: [16, 0] / 8832 eligible crossings.

- B4 T, pT1 GeV, q1: [0, 0] / 8064 eligible crossings.

- B4 T, pT1 GeV, q-1: [0, 0] / 8064 eligible crossings.

- B4 T, pT10 GeV, q1: [20, 0] / 8832 eligible crossings.

- B4 T, pT10 GeV, q-1: [16, 0] / 8832 eligible crossings.

Coverage software PASS does not pass the hermeticity gate: end differences remain.
No scattering, energy loss, hit inefficiency, reconstruction/occupancy or calibrated
resolution is modeled. Slopes must transport the separated stereo measurements
to a common reference plane;1D segmentation does not manufacture a second
coordinate or perform that correction.

## Failed attempts retained

The28-row/6 mm phi margin and36-row/20 mm margin controls miss paired coverage.
An exact helix launch-azimuth interval motivates the final32 mm reserve.
The wrong mounting edge had4696 native overlaps, plus duplicate ring role names
from assembly/solid name collisions; final free-edge placement and unique group
names fix them. The flat assembly exhausted ROOT voxel allocation; grouping by
stave preserves solids/tolerance. Initial native factory naming/load-path attempts
failed, followed by correction of CartesianStripX's default `strip` field.
A test asserted shear dominance at too long a span; the short-span fixture fixes
the premise while retaining shear scaling. Two exporter attempts failed on a
missing Path import and floating-point beam mesh endpoint indexing; both fixed.
No accepted historical artifacts/producers were overwritten.
