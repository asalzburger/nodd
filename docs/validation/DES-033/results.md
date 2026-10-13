# DES033 — turbine endcaps and LAYOUT-002 integration evidence

**DRAFT / PROTOTYPE; no engineering or response acceptance.**
Endcap scientific execution source464e3937808e8427f27ad2dcb3bed1bc717cb763;
Combined ECAL execution source7894524d3286b04978f45b61f0e52648c4b6d49c
contains the normal parent merge and same scientific files. Dirty flags identify
documentation/figure work; individual source/configuration/library and artifact
hashes are retained.
Drawing inputs pin that corrected source and the earlier tracker/magnet/barrel.

| Executed check | Result |
| --- | --- |
| LAr standard-library controls |28 passed |
| Complete isolated C++ build, including DD4hep component maps | PASS |
| Wheels / proper period placements / raw sensitive IDs |3 /4928 /9856 |
| Canonical reference keys / grouped-gap inverse checks |580 /4640 |
| Logical readout cells |601,600 per side;1,203,200 combined |
| Native endcap model mass with services, both ends |131.172858t |
| Full endcap overlaps/extrusions,10nm,seed41 |0 |
| Native endcap rays with independent interval gates |60 |
| Actual complete LAr ECAL-only overlaps,10nm,seed43 |0 |
| Combined signed-eta/fixed-phi material rays |405 |
| Sparse signed Geant4 transport |1 event and1 valid positive-energy saved hit per end |

Reports: [native](native.json), [combined ECAL](combined.json),
[positive transport](transport-positive.json), [negative transport](transport-negative.json),
[geometry summary](geometry-summary.json), [primary source hashes](sources.json).
[ECAL material/active paths](../../design/figures/DES-033/ecal-material-paths.png)
and [rear-board packing](../../design/figures/DES-033/endcap-board-packing.png)
are rendered native/model views. [Barrel results](../DES-032/results.md) remain
separate from the combined ECAL-only check.

## Independent assessment and corrections

SysArch and PhysVal read exact44ddd54aef096cff9d019dd6b9ee55c06f7b9d7b and
parent5f8c505e26f0f325f17d801583042849f06f62a2, without edits/native jobs.
They previously supplied design inputs: this is distinct-role implementation
assessment with acknowledged shared design provenance. SysArch tested139128
board pairs without overlap and checked axial/cooling/HCAL/forward interfaces.
PhysVal integrated24 turbine sections to1.007e-10 relative agreement and60
native active ray paths/counts to2.99e-11mm.

P2 source correction: source1.3mm total absorber includes0.1mm glue and0.1mm
steel, leaving1.1mm lead. Correct that lead core while retaining the deliberate
0.2mm mechanical-steel amendment, then recompute mass, references, overlaps,
rays and hits. The earlier139.557395t model is superseded by131.172858t;
this is a source correction, not tuning to a mass target.

P2 regression correction: endcap rays now gate PASS against independent
straight-face/cylinder intervals, actual gap counts, wheel-support paths,
finite/nonnegative material and active-LAr≤total-LAr. Eta4 has zero active path.
P2 interface disposition: the30mm unported Al rear annulus is a new conservative
proxy (1.953598t/end), not source rings/spokes or preserved mass. It blocks
electrode-to-board paths; openings/attachments are absent and require redesign
before routing qualification. P3 clarifies1495.9mm total HCAL depth includes
1485.9mm sampling and10mm cover. No agent supplies sign-off.

## Reproduction and limits

See [workflow](../../../tools/lar_calorimeter/README.md).
Native capacities verify actual Arb8 vertices/circular clipping and converged
axial section integrals; ROOT stochastic Boolean Capacity is not exact mass.
Mother exclusive mass subtracts actual daughter volumes. Raw gap IDs and
virtual rho/z cells remain distinct; calibration5/1/1 is not a shower-layer
or electronics bill. Cartesian rather than cylindrical lead taper is quantified
in the geometry summary.

The combined native union includes complete barrel/endcaps and their physical
cold-service proxies, excluding tracker, magnet, HCAL, FCal/muons and fields.
Its paths/material are directional geometry observations, not efficiency.
Sparse Geant4 retains one period in each of three wheels for each sign,
omits cryostat/services and begins a requested10GeV muon in middle-wheel LAr.
Exact argv, fixtures/source/log/ROOT hashes, observed seed42/FTFP_BERT, canonical
IDs and positive energies are checked. No whole-ECAL transport is claimed.

Cold thermal contacts, ports/support openings, headers/returns, vacuum/pressure
vessel, installed routing, manufacturing/strength, field, ACTS conversion,
digitization, showers, jets and particle flow remain open. Adverse258kW exceeds
200kW planning cooling. Partial-depth barrel/endcap transition remains; eta4
is uncovered. FCal/collar are empty future reservations with unresolved machine
and downstream beam-pipe interfaces.

Initial DDSim failed because library-only compilation omitted component maps;
building all isolated targets fixed registration. A new bath-volume test's
floating summation comparison was made dimensionless at1e-12 relative,
stricter than the existing1e-10 conservation gate. Earlier source/material
checks and actual failures remain curated in the paired journal.
