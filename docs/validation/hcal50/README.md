# Deep segmented HCAL around the restored LAr ECAL

2026-11-20. [DES-045](../../design/DES-045-hcal-restored-ecal-pion50.md)
implements the user-requested standalone HCAL study. DRAFT/PROTOTYPE; no
engineering sign-off or full-detector acceptance. The selected restored ECAL
context is pinned by the November18 selection, rather than the separate400mm
gap experiment.

![Fit and physical segmentation](figures/hcal-fit-segmentation.png)

The HCAL has60 layers of30mm Steel235, unchanged12mm DES036 common carriers
and1mm installation allowance, followed by a10mm rear cover:2590mm total
depth and1800mm steel. The front apothem3130mm, barrel half-length6260mm and
endcap front6760mm retain the restored ECAL interfaces and500mm rear service
gap. Barrel outer apothem is5720mm; endcaps end at9350mm, outer apothem5710mm.
The5950mm outer handoff is a reservation, with47.939mm margin after a50mm
service radius and20mm clearance beyond the barrel corner.

Readout retains21,032,064 individual tile channels in292,112 complete carriers.
Each carrier contains72 separate29.7×29.7×3mm recessed scintillator cores on
30mm pitch, reflectors, SiPM/electronics proxies, cold plate and cooling material.
The6.3mm board seam and service bay remain physical gaps. An anchored balanced
union preserves the exact disjoint sensitive regions while providing one native
context per carrier. Custom segmentation returns the original module/tile
addresses and positions. It does not replace the tiles with a continuous plane.

## Geometry and depth

The native material model gives Steel235 nuclear interaction length171.928151mm.
The nominal1800mm steel stack therefore provides **10.46949 nuclear interaction
lengths** in ROOT. The actual Geant4 transport material has interaction length
170.194699mm, corresponding to **10.57612 nuclear lengths** in1800mm steel.
These backend material conventions are recorded separately. The finite ROOT
face-centre ray confirms1800mm steel; the off-joint eta3,
phi0.123ray gives10.52152steel lengths. These exceed the prospective8length
nominal-depth screen. Total-material path sums additionally include real carrier
and support material and must not be confused with steel-only depth.

Exact fixed barrel sector seams remain pointing cracks: at phi=pi/16 and eta0,
±0.5or±0.8 the finite rays encounter zero steel and no sensitive cores. Endcap
quarter-joint rays at phi0 and |eta|3 see7.89114steel lengths because the
quarter seams rotate through the layer cycle. These adverse probes remain
explicit; the nominal-depth pass is not an all-angle8length or containment
claim. The uniform-phi shower sample includes the actual finite crack regions,
all zero-response primaries and all tails.

Full standalone native overlap checks inspect every distinct direct-daughter
mother, including the world. Reused placements are covered by their common
mother checks; no claim of combined tracker/ECAL/HCAL overlap validation is made.
ROOT core membership is checked against original leaf dimensions/transforms;
the actual converted Geant4 solids are independently checked against frozen
core/gap/recess regions. This second gate catches conversion discrepancies that
a ROOT-only check cannot detect.

## Response definition

The [prospective protocol](protocol.md) fixes10000origin pi-minus primaries with
50GeV total energy, independent uniform eta−3…3 and phi−pi…pi, no tracker,
beam pipe, ECAL, FCAL, solenoid or magnetic field. FTFP_BERT,0.7mm range cuts,
5mm charged step cap in active PSHost and event seeding are explicit.
The signal is raw scintillator deposited energy, with no Birks, optical,
SiPM, threshold, noise, time-window, digitization or calibrated response model.

Resolution plots use sample SD(R)/mean(R), ddof1, with R=Eraw/Etrue. Fifteen
signed-eta bins and fifteen folded-phi bins match the latest ECAL display. Phi
is a22.5degree barrel reference coordinate, because the whole-carrier endcap
packing has fourfold rather than16fold symmetry. The15% display padding on each
side repeats existing points and errors without adding statistical bins or
events. Full-phi controls are retained. Error bars are pointwise95% intervals
from1000joint whole-primary bootstrap draws, seed13001000, with30×30width
covariance. All zeros and tails are included.

Longitudinal profiles and terminal-six-layer activity diagnose rear shower
tails, but a shower can leave through a side or transition before those layers.
World-escaped kinetic energy excludes rest mass and nuclear invisible energy;
it is a separate diagnostic, not a calorimetric energy balance. A single50GeV
sample does not certify multi-TeV hadron containment.

## Reproduce and inspect

See [the exact commands](reproduce.md), [geometry source](../../../tools/hcal_response/README.md)
and [transport/closure source](../../../software/analysis/hcal_response/README.md).
Full XML, ROOT files, placements, event ledgers, build products and bulky logs
remain local under ignored build/hcal50. Published aggregates and plots suffice
for replotting; full native/readback/identity checks need the retained local
artifacts or a fresh source-bound reproduction.

Magnet/muon placement, FCAL routing, connected services, thermal/hydraulic,
mechanical and high-rate/radiation qualification remain separate work. This
HCAL proposal is not inserted into the maintained tracker+ECAL compact by the
standalone run. [Layout context](../../layouts/LAYOUT-002-tracker-3t-lar.md).
