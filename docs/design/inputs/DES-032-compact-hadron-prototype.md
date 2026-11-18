# DES032/033 — compact LAr hadron-collider prototype

2026-11-18. **DRAFT / isolated PROTOTYPE**, explicitly requested by the user.
Design input before implementation, based on main
`f3ece1d6a6816c8172dfa841d63e5424730e8228`. Maintained LAYOUT-002 remains
unchanged. No human design sign-off or pressure-vessel qualification is implied.

## Requirements and retained features

User request: fit around the tracker/solenoid baseline, respect vacuum/bath/wall
needs, provide sufficient electromagnetic depth for a 14 TeV hadron-collider
option, preserve ALLEGRO inclination/relative sampling radii, and repeat matched
10k electron controls. Existing request for twelve transport workers persists.

**FACT — DES026:** retain the 1640 mm magnet assembly reservation and 60 mm
external interface, even though the computed vessel radius is 1558.656 mm.
**NODD DESIGN CHOICE:** use a 1700 mm warm bore. Retain the inherited front
10 mm warm wall, 49 mm vacuum, 3.8 mm cold wall and 10 mm bath: sampling starts
at 1772.8 mm. These are explicit simulation budgets, not certified vessel minima.

**NODD DESIGN CHOICE:** preserve barrel 50.18° inclination, the exact ratio
2578.3/2172.8 between sampling outer/inner radii, and all normalized compartment
boundaries. Scale the original compartment path lengths by the common radius
factor; leave material densities, steel/glue and 1.2 mm electrode unchanged.
Sampling back becomes 2103.649779 mm. Retain endcap 49° inclination and all wheel
radial boundaries and relative proportions.

## Electromagnetic depth and sampling choice

**FACT — SRC-CMS-ECAL-PERFORMANCE-2013, §2:** the CMS LHC calorimeter has
25.8 X0 barrel /24.7 X0 endcap depth. This is a precedent, not an nODD acceptance
requirement. **NODD DESIGN CHOICE:** screen for at least 25 X0 **in sampling**
for fully traversed interior directions, separating upstream walls and rear
services from useful sampling. Partial-depth transitions and support bands must
remain explicitly visible; the target is not claimed for every direction.

Uniformly shrinking physical plates/gaps is rejected. **NODD DESIGN CHOICE:**
1408 barrel periods and 2.6 mm Pb balance physical gap space and sampling count.
The 1.2 mm multilayer electrode is retained; thinning it without a new physical
readout design is not justified by the ALLEGRO source. The initial single LAr
gap is approximately 0.484 mm. Standard-library phase screens estimate
25.62–26.15 sampling X0; actual ROOT material lengths must replace these estimates.
The FCC-hh report's 0.5 mm endcap gap (§2.2.2, PDF25) establishes a studied scale,
not fabrication/space-charge qualification of this nODD model. Relative to the
old barrel, fewer periods and thicker Pb may degrade sampling precision; that
is a measured question, not an assumption used to declare success.

**NODD DESIGN CHOICE:** increase endcap sampling depth 450→650 mm while keeping
Pb1.1 mm at the wheel reference, PCB1.3 mm, period counts, radii and 49° angle.
Retain the full rear service bath by extending the cold/warm back by200 mm.
The initial600 mm candidate had roughly28–30 X0 in selected core directions,
but the finer native angular scan found24.3896 X0 at a wheel-support direction
nearη2.7. Increase to650 mm before any shower-response analysis to address this
material-depth shortfall; revalidate the native phase/support scan and gaps. The Cartesian-versus-cylindrical Pb taper approximation remains;
its maximum difference grows and must be retained in native audit evidence.

## Vessel, bath, services and interfaces

**NODD DESIGN CHOICE:** retain 30/49/2.7 mm rear cold/vacuum/warm walls and
increase rear bath170→210 mm. At the smaller circumference, the original twelve
75 mm boards per sector overlap neighbours. Ten columns at80 mm pitch and three
banks at sampling-back offsets15/60/105 mm preserve at least3M planning capacity:
7392 slots /3,784,704 channels. Physical board shapes, fifteen axial rows and
sixteen H-rings are retained. N2 pipe centre is sampling-back+197 mm, leaving
about12.06 mm from the largest board corner and3 mm to the bath boundary.
Warm outer radius becomes2395.349779 mm. Native containment/overlaps are required.

The external bus remains3029 mm because unchanged endcap radii govern it.
**NODD DESIGN CHOICE:** use actual400 mm bend radii for80/100 mm jackets,
respecting the ≥4OD rule. The corresponding envelopes896.8/916.8 mm require a
1000 mm front reservation. Translate the complete endcap +200 mm, then extend
its rear for the added sampling depth. Warm front/back5100/6260 mm; sampling
front/back5210/5860 mm. Retain500 mm rear service break: HCAL endcap front6760 mm
and wrapping barrel half-length6260 mm are design-only consequences. Existing
HCAL radial front3130 mm and sampling depth1495.9 mm are retained. No HCAL solid
or baseline magnetic solution is changed in this isolated ECAL study.

Ports, seals, relief, hydraulic margins, buckling, thermal contraction and
load paths remain engineering gates. Planning3M powered channels at40 mW is
120 kW before static loads. Fully populating all slots would require151.4 kW
at40 mW/channel, exceeding that reference; spare capacity is not proof of
thermal headroom. No radiation, pileup or electronics acceptance is transferred.

## Prospective validation

Freeze source/configuration before production. Require native construction,
containment/overlaps, exclusive mass/shape/transform and raw-ID/readout audits,
and angular material maps split into upstream/sampling/downstream contributions.
Check barrel phase variation, supports and both transition shoulders. Compare
old/new path classes on common directions; do not move the original response bins.

Repeat exact saved10k electrons, E10–80 GeV, η−3…3/fullφ, twelve workers,
event seeds133812341, FTFP_BERT/0.7 mm cuts/5 mm active charged-step cap,
ECAL-only B=0, all events/zeros/tails. Preserve serial/MT and readback controls.
Analyze paired Δ[SD(R)/mean(R)] with1000 shared whole-event bootstrap replicates;
retain angular/energy controls, distributions, means, tails and covariance.
No noninferiority threshold is invented. A statistically compatible result
cannot prove equality or realistic digitized resolution. Low-energy controls
and material depth alone do not certify multi-TeV containment or hadron/jet,
pileup and radiation performance. Additional high-energy/leakage qualification
remains explicit in the results.


## Measured limitation and conditional thicker-annulus alternative

The completed matched10k controls do not establish preserved precision. Even
exploratory held-out eta-gain calibration gives core-barrel CV 2.43→4.30% and
broad-endcap CV 3.09→7.36%; see the full validation report. The strict ratio
candidate remains an adverse control, not a selected replacement baseline.

**INFERENCE / conditional design screen:** CaloTech assessed source
5a8814fc1947b16446aa0c9e3c73714ad06837b7 read-only. If relative sampling radii
means normalized compartment fractions rather than fixed global Rout/Rin,
a thicker option could keep Rin=1772.8mm, inclination50.18°, restore Pb1.8mm /
steel0.2mm / glue0.1mm / PCB1.2mm and use1248 periods with Rout=2350mm.
The original normalized radial compartment fractions are preserved through
Rnew=1772.8+(2350−1772.8)f_old, then converted to electrode path increments.
This changes Rout/Rin from1.186626 to1.325587. It is not implemented or selected.

The analytic exact-chord screen uses approximate radiation lengths in mm:
Pb5.612, LAr140, steel17.5, glue180, PCB180. At eta0,128 phases give
26.804–27.318 sampling X0; inner single gaps1.207/1.209mm, outer3.169/3.174mm.
A finite20-direction handover screen over abs(eta)1.2–1.6 with64 period-phase
probes/direction, retained650mm endcaps and correctly truncated barrel chords
has minimum31.381X0. These are approximate-material, finite probes; actual
native material lengths, complete angular/dead-material scans and transport
must precede any performance claim. An earlier rough transition-shortfall
warning omitted cosh(eta); its15–17X0 estimate was incorrect and is superseded.

Retaining210mm rear bath and wall/vacuum thicknesses gives warm outer2641.7mm,
still188.3mm inside the original2830mm. Board fronts2365/2410/2455mm and N2
centre2547mm retain the screened bath clearance; the1000mm front reservation
exceeds an854.08mm two-arc100mm-jacket screen with400mm bends. Actual ports,
supports and routing remain unqualified. Logical barrel channels1,979,328;
phi-cell angle changes to2pi/624 while inner physical pitch stays about17.85mm.
Larger outer gaps and changed granularity require fresh calibration and a new
matched10k control. The endcap precision issue remains a separate design problem.
