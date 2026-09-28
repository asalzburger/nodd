# DES-006 input — PhysVal independent layout screen

- Date: 2026-09-18.
- Status: **DRAFT / PROTOTYPE — idealized calculations, no human sign-off**.
- Role: Physics and Performance Validation (`PhysVal`); coordinates with
  `SysArch`, `TrackTech` and `SoftEng`.
- Governing scope: [DES-005](../DES-005-tracker-system-plan.md), its
  [validation contract](DES-005-tracker-system-physval.md),
  [DES-003](../DES-003-global-envelopes.md) and
  [ADR-006](../../decisions/ADR-006-global-envelope-and-field-hypotheses.md).
- Numerical inputs: [candidate catalogue](../DES-006-layouts.json).

## Recommendation

Carry both candidates into module-aware coverage and common-response parametric
studies. Use A as the smaller-area control and B as the forward-redundancy
challenge. **Do not select B merely because it crosses more ideal surfaces.**
B increases information opportunities but cannot remove the envelope's short
forward bending lever arm; its larger pixel inventory adds unresolved material,
cooling and service demands. Both candidates have a pixel transition weakness
that deserves a dedicated variation before choosing either.

The requested coverage remains `|eta| < 4`. Endpoint probes at exactly `|eta|=4`
test boundary margin; they do not redefine the strict requirement. A successful
ideal crossing is neither a reconstructed track nor a demonstrated physics
acceptance. No minimum station count, resolution limit or beamspot distribution
has been approved for this comparison.

## Provenance and calculation contract

**NODD DESIGN CHOICE — human-directed constraint:** retain the tracker host
`0.025 <= r <= 1.140 m`, `|z| <= 3.150 m` and fixed `|eta| < 4` investigation
requirement from DES-005. The host's inner radius is not an active sensor radius.

**NODD DESIGN CHOICE — proposed, no approving humans:** candidate dimensions,
ideal complete cylinders/annuli, origin and longitudinal stress vertices
`z_v = -0.150, 0, +0.150 m`, and the deterministic grid `eta=-4..4` in steps
of `0.001`. These discrete vertices are stress probes, not Gaussian quantiles or
a certified luminous region. The initial angular scan is axisymmetric; it has
no evidence about azimuthal cracks or a transverse beamspot.

**FACT — reused source observations:** the source evidence ledger in the
[tracker envelope input](DES-003-tracker-envelope-input.md), citing
`SRC-ATLAS-TDR-030` §2.1–2.1.2 and `SRC-CMS-TDR-014` §3.1, distinguishes
pixel/strip reach, states study-specific luminous-region assumptions and supports
progressive layout studies. These facts motivate the protocol; those detectors'
beamspot widths and hit targets are not nODD inputs. Source identities remain in
the [manifest](../../../reference/manifest.yaml); no new external numerical
detector parameter is introduced by this input.

**INFERENCE — independent geometry:** from `eta=-ln(tan(theta/2))`, a straight
ray from the beam axis satisfies `z=z_v+r*sinh(eta)`. A barrel is crossed when
that z lies within its half-length. A disk is crossed when
`r=(z_disk-z_v)/sinh(eta)` is positive and lies within its annulus; at `eta=0`
the ray crosses no endcap. Mirror both disks and vertices. Count a long-strip
stereo pair as one station with two one-dimensional measurements, never as two
independent two-dimensional hits. The reported lever arm is the difference
between largest and smallest crossed radii, not the detector outer radius.

## Independent results and their implications

The calculations below use the candidate tables supplied by TrackTech, before
consulting the shared study output. Bounds include their geometric edges and
omit finite sensor thickness, module tiling, dead edges and scattering.

| Positive eta; vertex z [m] | A pixel / strixel / stereo-pair stations | B pixel / strixel / stereo-pair stations | A / B transverse span [mm] |
| --- | --- | --- | --- |
| 0; 0 | 4 / 4 / 2 | 4 / 4 / 2 | 986.00 / 986.00 |
| 2.5; 0 | 5 / 6 / 0 | 8 / 6 / 0 | 466.81 / 466.81 |
| 3; 0 | 6 / 4 / 0 | 12 / 4 / 0 | 268.46 / 272.45 |
| 3.5; 0 | 9 / 0 / 0 | 11 / 0 / 0 | 146.29 / 146.29 |
| 4; 0 | 7 / 0 / 0 | 9 / 0 / 0 | 72.19 / 72.19 |
| 4; +0.150 | 6 / 0 / 0 | 8 / 0 / 0 | 61.19 / 66.69 |

**INFERENCE:** over the full signed-eta grid, A's minimum ideal station count is
seven at the origin and six at either shifted vertex; B's corresponding minima
are nine and eight. At the most forward edge these stations are all pixels.
These minima describe this sampled ideal geometry; they are not efficiency or
redundancy acceptance thresholds.

**INFERENCE — transition warning:** both candidates have only three pixel
stations at origin-grid points `eta=1.880..1.894`. With `z_v=+0.150 m`, both
have three at `eta=1.581..1.647`; A additionally has three at
`eta=1.952..1.965`. The negative-side counterparts follow reflection symmetry.
These intervals quote sampled points, not analytically determined continuous
boundaries. Total station counts include strips there, so this does not prove
unreconstructibility. It identifies a pixel-seeding and vertexing vulnerability
to study with first-disk placement/width, barrel extent and actual active edges.

**INFERENCE — forward limit:** `sinh(4)=27.2899`. At `z=3.150 m`, the largest
prompt eta-4 radius is `115.43 mm`; a same-side `+150 mm` vertex reduces it to
`109.93 mm`. At the last proposed disk, `z=3.070 m`, the stressed crossing is
`107.00 mm`. Enlarging that disk's outer radius from `200` to `320 mm` does not
move the eta-4 hit. B's extra intermediate disks chiefly improve redundancy;
their wider annuli buy mid-forward measurements. Far-forward momentum precision
must be evaluated separately from hit count.

For a `35 mm` active inner edge, a stressed eta-4 ray first reaches that radius
at `z=1.105 m`; this explains why the `1.100 m` disk narrowly misses it.
An inner-edge or beam-pipe change of only a few millimetres matters. Actual
beam-pipe profile, module rim and support clearance are required before treating
this aperture as buildable.

**INFERENCE — area cost:** ignoring gaps, overlaps, stereo duplication and all
passive material, summed pixel cylinder/annulus area is `4.902 m^2` for A and
`8.526 m^2` for B. Their two-endcap contributions are `2.193` and `5.817 m^2`:
B has about `2.65` times the disk area and `1.74` times the total pixel area.
These are geometric resource proxies, not module counts, costs or power estimates.

## Independent measurement-only curvature control

**INFERENCE — small-curvature transverse model:** for uncorrelated transverse
measurements, write `y(r)=d0+phi0*r+0.5*kappa*r^2`, with free `d0`, `phi0` and
`kappa`; no vertex prior is applied. Each information-matrix row is
`H_i=(1,r_i,r_i^2/2)` and its weight is `1/sigma_rphi_i^2`. The covariance is
`C=(H^T W H)^-1`, giving
`sigma(q/pT)=sqrt(C_kappa,kappa)/(0.299792458*|B|)` in `GeV^-1` for radii in
metres and field in tesla. This is the uniform-solenoid small-curvature limit,
with scattering and all other process noise absent.

The response inputs are the explicitly provisional C04 scenario in the
candidate catalogue: pixel `50/sqrt(12) micrometres`, strixel `20 micrometres`,
and the co-located symmetric stereo pair's effective transverse precision
`20/(sqrt(2)*cos(0.020)) micrometres`. This control uses only the transverse
coordinate; it does not validate the second coordinate or a stereo reconstruction.

| eta; vertex z [m] | A sigma(q/pT) [GeV^-1] | B sigma(q/pT) [GeV^-1] | B/A |
| --- | --- | --- | --- |
| 0; 0 | 0.0001357756 | 0.0001357756 | 1.0000 |
| 4; 0 | 0.02437237 | 0.02346316 | 0.9627 |
| 4; +0.150 | 0.03539294 | 0.02781998 | 0.7860 |

At the origin, the free transverse intercept uncertainty is `10.626 micrometres`
centrally for either candidate and `60.233 / 55.310 micrometres` at eta 4 for
A/B. Those are ideal transverse-model uncertainties, not validated reconstructed
impact-parameter resolutions.

The forward curvature result changes the interpretation of hit redundancy:
despite seven versus nine origin stations, B improves this measurement-only
curvature uncertainty by only about `3.7%`. Under the positive-vertex stress
its improvement is about `21.4%`, because the extra earlier disk protects the
available span. Both remain far less constraining than the central geometry.

At `pT=100 GeV`, multiplying the origin eta-4 inverse-momentum errors by pT
would give `2.44 / 2.35`. **These are not meaningful Gaussian fractional-pT
resolutions:** the reciprocal transformation is strongly nonlinear at such
uncertainty. Retain inverse-momentum uncertainty as the primary diagnostic and
study fitted curvature, tails and charge assignment before any performance
claim. No approved forward momentum requirement is available, so the result
exposes a limitation without declaring acceptance or failure of a physics target.

The retained [independent control](../../../tools/tracker_layout/covariance_control.py)
used NumPy `2.5.3` in the existing envelope-study environment and the shared layer
catalogue. Its [compact evidence](../../validation/DES-006-covariance-control.json)
records input/code hashes, starting project revision, dirty-worktree state,
Python/NumPy versions, exact command, units and all crossed radii/precisions.
An SVD covariance calculation
agreed with the normal-matrix inverse to a maximum relative diagonal difference
of `1.69e-13` across both candidates, eta `0/4` and vertex `0/+0.150 m`.
This checks the small numerical calculation only. Its comparison with IdRes
requires zero material, the same measurement/vertex assumptions and a sufficiently
small-curvature probe; finite-curvature and five-parameter effects must be
distinguished from implementation mistakes.

### Comparison with executed IdRes controls

The [retained IdRes evidence](../../validation/DES-006-idres-results.json)
contains actual output at `B=3 T`, `pT=100 GeV`, no vertex prior,
with material allowances multiplied by `1e-6` and `1e-8`. Exact zero material
encounters an upstream `log(0)` issue, so these two positive controls test
convergence toward the independent zero-material result. Both factors produced
identical printed values at the points below. They are numerical fixtures,
not physical material hypotheses.

The executable uses `0.3` for the magnetic conversion where the independent
control uses `0.299792458`. It prints inverse-pT uncertainties in `TeV^-1`
to three decimal places. Compare the same convention before interpreting a
discrepancy; dividing the printed numbers by `1000` gives `GeV^-1`.

| Candidate; eta; vertex z [m] | Independent control with IdRes's 0.3 convention [TeV^-1] | IdRes near-zero output [TeV^-1] |
| --- | --- | --- |
| A/B; 0; 0 | 0.135682 | 0.136 |
| A; 4; 0 | 24.355506 | 24.356 |
| B; 4; 0 | 23.446930 | 23.447 |
| A; 4; +0.150 | 35.368454 | 35.368 |
| B; 4; +0.150 | 27.800731 | 27.801 |

All agree within half of the last printed `0.001 TeV^-1` unit; the maximum
absolute difference is `0.000495 TeV^-1` after rounding upward. This is a
reporting-precision consistency check, not a detector-performance tolerance or
validation of IdRes's material model and second-coordinate covariance.
The independent control artifact retains the IdRes artifact hash and all
16 comparisons (both candidates, eta `0/4`, vertex `0/+0.150 m`, two tiny
positive material factors); all satisfy the printing-resolution check.

This control also caught a real setup failure: the first multi-valued field
table evaluated the `2/3/4 T` entries with the final `4 T` value, giving a
spurious `0.75` ratio to the expected `3 T` uncertainty. SoftEng corrected the
run configuration to one field per execution and reran the controls. Agreement
above applies to those corrected runs. Keep this limitation in the installation
and adapter documentation; a successful executable invocation alone did not
establish a valid field scan.

The final corrected artifact also separates upstream hit counters from physical
station counts. Its central `upstream_hit_count=16` consists of four pixel
entries plus twelve strip-coordinate entries; the corresponding effective count
is ten stations (`4 + 12/2`). It is not sixteen physical sensitive stations.
PhysVal independently checked **all 243 baseline origin-profile rows per
candidate**, covering 81 eta points and three momenta: effective station counts
agree exactly, with no exceptions.

The independent normal-thickness incidence sum also checked all **81 material
eta points per candidate**. Each pixel allowance is counted once, each strixel
allowance once, and each long-strip pair's `2% X0` allowance once. The central
sum is `4*1% + 4*1.5% + 2*2% = 14% X0`, matching IdRes. Across both full
profiles the largest absolute difference is `4.872e-7` percentage points of
`X/X0` (rounded upward), within half of the reported `1e-6` percentage-point
last digit. No count mismatch or double-counted stereo-pair material was found
in these baseline profiles. This validates the adapter's ideal material
accounting at reporting precision; it does not validate real material
composition, omitted services or scattering physics. The control artifact
retains counts, maximum discrepancies and the exact IdRes source-artifact hash.

### Material and momentum change the candidate ranking

The executed IdRes model gives the following at uniform `3 T` with nominal C05
material allowances. These are parametric covariance results, with upstream
straight-ray intersections and ideal measurements; they do not include module
gaps, reconstruction losses or completed physical material inventories.

| eta; vertex z [m]; pT [GeV] | A sigma(q/pT) [GeV^-1] | B sigma(q/pT) [GeV^-1] | Interpretation within this model |
| --- | --- | --- | --- |
| 0; 0; 1 | 0.005241 | 0.005241 | Identical central control |
| 3; 0; 1 | 0.019393 | 0.022368 | B is about 15.3% worse despite extra pixels |
| 4; 0; 1 | 0.057425 | 0.061435 | B is about 7.0% worse |
| 4; +0.150; 1 | 0.066674 | 0.065541 | B is about 1.7% better |
| 4; 0; 10 | 0.024916 | 0.024144 | B is about 3.1% better |
| 4; 0; 100 | 0.024361 | 0.023454 | B is about 3.7% better; report inverse momentum |

The eta-4 `pT=1 GeV` probe has total momentum `27.308 GeV`; it must not be
described as a `1 GeV` total-momentum particle. This distinction also prevents
misreading the relative size of scattering and measurement errors across eta.

In the positive-vertex eta-4 `pT=1 GeV` case, halving all material allowances
gives A/B `0.052575 / 0.049579 GeV^-1`, while doubling gives
`0.089207 / 0.089924 GeV^-1`. B's relative advantage therefore changes from
about `5.7%` better to `0.8%` worse across these declared sensitivity controls.
At the origin it remains worse at this pT for all three material factors.
This supports retaining both candidates and testing narrower extra pixel rings:
additional measurements do not automatically repay their material cost.
Material-factor scenarios are not confidence intervals. A component-resolved
material model and reviewed kinematic priorities are needed before weighting
these tradeoffs into a selection.

## What a valid resolution/material comparison must retain

Use the same response, material and field assumptions for A and B before any
candidate-specific optimization. Name every provisional per-layer allowance and
missing beam-pipe, cooling, support or routed-service contribution. Extra layers
must bring their associated material; an equal-total-material comparison is a
separate artificial control. Material before useful measurements matters as well
as the integrated total. In the straight-ray thin-layer limit, barrel normal
thickness scales by `cosh(eta)` along the track, while disk thickness scales by
`1/|tanh(eta)|`; near-grazing, finite-size geometry must replace that limit.

The proposed `pT=1, 10, 100 GeV` and uniform `B=2, 3, 4 T` grid is a
**NODD DESIGN CHOICE — screening scenario**, not an operating spectrum or field
solution. Report `p=pT*cosh(eta)` alongside pT: at eta 4 the three total momenta
are about `27.3, 273, 2731 GeV`. Show material factors `0.5, 1, 2` as sensitivity
controls without calling that range a measured uncertainty. After global factors,
vary component groups and locations; concentrated services cannot be assessed by
a uniform multiplier. A central field value does not certify forward Bz or Br.

Distinguish known-vertex and free-vertex fits. Preserve failed/singular fits and
missing parameters in outputs. Establish exactly which coordinates IdRes uses,
whether stereo pair axes/correlations are represented, and what material/field
model it supports before interpreting any returned covariance. Never equate
short-strip granularity with a full pixel measurement or silently replace a
stereo pair with two isotropic hits. A one-projection fit can be informative if
explicitly restricted; it cannot establish the full five-parameter covariance,
pattern-recognition efficiency or impact-parameter resolution in both planes.

## Priority and unresolved-input register

| Priority | Discriminating next action | Required input / decision owner |
| --- | --- | --- |
| 1 | Reproduce station/coordinate counts, aperture-edge losses and pixel-transition minima with bounded modules; test local placement changes before accepting either layout | TrackTech/SoftEng; pixel module active masks and clearances from existing DES-001 work; beam-pipe/support profile from SysArch. Ideal variants can proceed now; physical clearance closure is blocked. |
| 2 | Audit IdRes coordinate and covariance semantics; compare common-response A/B resolution with material/field sensitivity and independent limiting cases | SoftEng/PhysVal. Tool audit can proceed now; quantitative performance acceptance needs human thresholds and realistic response/material inputs. |
| 3 | Quantify B's extra material/services against its mid-forward information gain; carry A as the control and consider narrower additional pixel rings as a bounded follow-up | TrackTech/SysArch; pixel power/cooling, supports, short-strip occupancy and route inventories are not ready. No preferred technology boundary can yet be frozen. |
| 4 | Replace stress vertices with a sourced luminous distribution and examine conditional tails, signed eta, azimuth and off-axis vertices | PhysVal/humans; distribution, crossing angle and tail convention remain open. Do not delay all geometry debugging while waiting. |
| 5 | Repeat with available physical vector fields, then fast fits and realistic occupancy/pattern recognition | DES-004 field providers; reconstruction/response and event inputs remain incomplete. Uniform-field curves do not resolve magnet selection. |

Human follow-up questions: which momentum/eta regions and physics uses set the
resolution and efficiency priorities; how much pixel redundancy is required near
transitions; what luminous-region tails must be covered; what resource penalty
would justify B; and which timing use case must be demonstrated? Timing remains
a follow-up comparison with and without time information and with its hardware
material retained. No time measurement or timing benefit is present in these
spatial layouts.

## Verification performed

PhysVal independently evaluated the stated straight-ray equations against both
candidate tables using a temporary Python script, with 8,001 signed-eta points
per vertex and three vertices per candidate, and separately recomputed annulus
and cylinder areas. The retained NumPy calculation evaluated the measurement-only
transverse covariance and compared normal inversion with SVD. Three independent
tests passed under both the system Python and the existing envelope environment:
vertex/reflection/aperture geometry, the exact three-point second-difference
curvature variance, and precision scaling/rank-deficiency handling. NumPy is
optional for the standard-library test runner; numerical tests explicitly skip
when unavailable, while the geometric check still runs. These analytic
checks use no random sampling. Their formulas,
grid and candidate inputs are specified above so the shared study can reproduce
them. The IdRes comparison uses SoftEng's executed and retained results; PhysVal
did not independently build or invoke that executable. No ACTS propagation,
material transport, DD4hep construction, Geant4 run or reconstructed-physics
validation is claimed. The coordinating report records actual tool runs and
retained evidence.
