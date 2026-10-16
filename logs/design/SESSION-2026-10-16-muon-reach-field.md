# SESSION-2026-10-16-muon-reach-field

## Scope and evidence

Contemporaneous bounded analysis of LAYOUT-001 plus open HCAL PR81/84/85,
from main5b4e5d9e563505aea17e9b792458708c3175ec4a in a clean isolated
codex/muon-reach-field-study checkout. Existing user changes in other checkouts
were preserved. No production geometry integration or external publication.

## Selected conversation

User requested the current baseline01 with unmerged HCAL prototypes, a reasonable
low-momentum muon threshold using3T tracker/IdRes and calorimeter scattering/loss,
and ATLAS-like muon field sizing assuming180um precision, with MDT cross-check.
Assistant interpreted the combination as an isolated PROTOTYPE numerical study.

## Decisions and outcomes

MUON-001 retains component revisions, material paths, mean-loss transport,
72IdRes covariance cases, field equations and plots. Central candidate working
points5/10GeV are conditional; no reconstruction efficiency measured. ATLAS MDT
single-tube measurement81.7+/-2.2um corrects the180um benchmark;180um is retained
as effective station error. Upstream calorimeter scattering is separated from
internal spectrometer scattering. No field moves their intrinsic/MS crossover.

Assignments were explicitly supplied to generic children, not verified native
profile loading. Initial read-only discovery preceded the full role contracts;
no child wrote repository files. C1 SysArch/CaloTech read pinned LAYOUT-001 and
HCAL revisions and supplied finite material intersections; T1 TrackTech/SoftEng
ran pinnedIdRes on current nominal layer proxies; M1 MuonTech/PhysVal checked
primary ATLAS/PDG sources. M2 separately reviewed fixed dirty-file hashes and
numerical/scientific interpretation. See docs/validation/MUON-001/review.json.

The existing ACTS Spack preflight reported changed setup/lock fingerprints.
Direct standaloneIdRes and an existing NumPy/Matplotlib interpreter were used;
no ACTS/DD4hep/Geant4 qualification or shared dependency modification is claimed.

## Commands and validation

Fetched origin and read current openPR revisions with gh. Ran tracker_idres.py,
hcal_material.py and study.py with explicit paths recorded in MUON-001.
72IdRes cases agree with independentGLS within half printed precision. Five
primitive/four native module ray comparisons, transport convergence, high-p
Highland limit and1/B controls passed. PNG/SVG visually inspected.
Initial project validation rejected a prose deliverable as an unsafe URL;
changed it to the report path and reran successfully. Independent review found
an IdRes source-argument metadata bug and mismatched paper titles; fixed these,
regeneratedIdRes and verified closure. No numerical conclusion changed.
Session/project validators and session summary run at closeout. No full transport,
occupancy, straggling, curved muon acceptance or reconstruction efficiency test.

## Changes and revision links

Tools/muon_study; docs/validation/MUON-001 evidence/report; source manifest;
TASK-B-MUON evidence; this session pair. Full file inventory in pairedJSON.
No commit, push, PR, sign-off or production baseline change was requested.

## Token accounting

No exact disjoint client-reported per-turn token counters were exposed for the
root or children. Usage remains empty, not zero. No private client state read.
Summary reports observed project coverage separately from missing measurements.

## Follow-up

Specify station geometry, field and material maps, collector/cable/support
material, chamber resolution/alignment and reconstruction criteria; then test
transport, straggling, efficiency and momentum resolution against the candidate
working points. Barrel/endcap transition and high-eta bore require separate work.
