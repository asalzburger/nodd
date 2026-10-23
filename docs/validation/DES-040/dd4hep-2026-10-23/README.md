# Muon chamber/toroid DD4hep realization — 2026-10-23

The isolated **PROTOTYPE** implements the first stage of [issue92](https://github.com/asalzburger/nodd/issues/92) and the envelope-overlap step of [issue93](https://github.com/asalzburger/nodd/issues/93). The exact PR90 source is `cae3a72f3b1c98edaf9bc28a84d019142606ba25`, geometry SHA256 `7b2b0de109a5ec4a908e4f91a05e9caf9bdedfa6141b09d7c82a98b56e7cfc02`.

The checked-in [compact XML](../../../../prototypes/muon/compact/muon-system.xml), [materials](../../../../prototypes/muon/compact/materials.xml), [expected inventory](../../../../prototypes/muon/compact/expected.json), [C++ factory](../../../../prototypes/muon/Muon.cpp) and [reproduction commands](../../../../prototypes/muon/README.md) are reviewable together. The root detector build is unchanged. DES039/DES040 remain DRAFT; this is no engineering sign-off or production integration.

| Executed check | Result |
|---|---|
| Standalone C++20 factory build | PASS, DD4hep1.38 / Geant4 11.4.3 |
| Source/native chamber vertices, transforms and IDs | PASS for936; maximum vertex residual2.51215e-15m |
| Native coil CSG primitive inventory/dimensions/poses | PASS,288 primitive instances across3 shared groups representing36 source coils |
| Exact-mask/native-solid occupancy probes | PASS,25248 probes, zero mismatches |
| Installed `checkOverlaps` plus explicit native overlap list | PASS, zero illegal overlaps/extrusions at0.00001mm numerical tolerance |
| Geant4 requested gun transport | PASS,1000 20 GeV with DDSim `uniform` (flat theta/azimuth) gammas, seed92393, FTFP_BERT |
| ROOT persisted event count | PASS, native `EVENT` tree1000 entries |
| Export and failure-gate unit controls | PASS,12 tests |

The [run report](run.json), [native geometry audit](geometry-validation.json), [stock overlap log](checkOverlaps.log), [compressed DDSim log](ddsim.log.gz), [environment identity](environment.json) and [failed-attempt record](attempts.json) retain actual execution. The initial successful run records a dirty source revision together with exact file hashes; this does not claim those changes were already committed. The [committed-source replay](committed-replay/run.json) passes with source `1f0e98c90c4eb7ff33e562af032b0f6ae6981cf0` and `source_dirty=false`, using the checked-in compact bundle; its [native audit](committed-replay/geometry-validation.json) and [DDSim log](committed-replay/ddsim.log.gz) are retained separately. Independent assessment follows this evidence freeze.

All chambers and warm reservations are **nonsensitive Air**. This tests exact shapes, native construction, geometry conversion and transport topology; it does not validate coil/chamber mass, realistic photon conversion, drift response, muon efficiency or momentum resolution. HCAL,484 frame bodies and magnetic fields are absent from this compact. Native zero-overlap evidence does not rerun the older full-system support/service certificates or convert the source50mm clearance requirement into an engineering acceptance.

The DD4hep stock script passes its tolerance directly to ROOT and always exits zero after printing, including when overlaps exist. Here `dd4hep.mm=0.1` ROOT units; the runner converts physical tolerance to1e-6 ROOT units and separately rejects a nonempty native overlap list. Source/native solid and transform checks supplement the ROOT surface-overlap calculation; sampled occupancy alone does not prove separation.

DDG4 normally skips persistence when `G4HCofThisEvent` is null in a geometry without sensitive detectors. [MuonEvent.cpp](../../../../prototypes/muon/MuonEvent.cpp) supplies an empty event-owned container before transport. No hit collections are created. The native ROOT writer records MC truth, and the tracker-region user particle handler is disabled because no tracker/hits are defined. Earlier completed runs without persisted events were rejected by the output-count gate; their failures remain recorded.

The [SysArch assessment](interface-review.md) checks the exact source interfaces in a separate agent context. The [independent PhysVal review](physics-review.md) reproduces the native audit and12focused tests, verifies1000parentless20GeV PDG22primaries in the digest-matched ROOT file, and finds no implementation-blocking defect for this bounded stage. Its sole angular-distribution wording finding is resolved by the [exact-revision amendment check](physics-amendment.json). No agent supplies human approval.

Issue93's drift-tube filling remains a separate next stage after this envelope gate. Its literal approximately30mm radius differs from the ATLAS approximately30mm-diameter precedent. Two three-layer stacks at30mm radius need at least327.846mm depth, before inter-stack spacing/support/services, within the500mm envelope. Some endcap tips are only17.143473mm wide. A bounded internal model must document finite tube containment, inactive tips, gas/wall/pitch/separation, readout identifiers and sensitive response. No physical choice is silently inherited from the outline study.

The requested `--gun.distribution uniform` is flat in polar theta and azimuth. DDSim uses the separate `cos(theta)` option for equal-solid-angle directions; this run does not use that option and supplies no solid-angle coverage estimate. See registered source `SRC-DD4HEP-GUN-1.38`, [Gun.distribution](https://github.com/AIDASoft/DD4hep/blob/v01-38/DDG4/python/DDSim/Helper/Gun.py#L74-L79).
