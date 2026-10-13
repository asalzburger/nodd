# DES028 — Executed cassette prototype checks

2026-10-12. **DRAFT / PROTOTYPE**. Starting revision ed30e63fb0ab30b66d4084a9058906929006f792.
Execution used an uncommitted worktree; exact source/config/compact/library
hashes are retained in [native.json](native.json) and [budgets.json](budgets.json).
The complete inventory is reproducible from the exporter; its hash is retained.

Existing node runtime verified: DD4hep1.38, ROOT6.40.04, Geant4 11.4.2;
Spack Python3.14.5. Independent controls used system Python3.14.6. All13
Geant4 datasets installed. Skill preflight reported setup/lockfile fingerprint
drift; actual imports, installed prefixes, versions and datasets were checked.
CMake policy/CLHEP warnings remained visible; no shared software was modified.

Seven standard-library controls pass. Native construction passes:859 material
parts,148 unique sensitive IDs,1168 cell round trips, all capacities/densities,
constituent elemental mass fractions and total masses agree. Restricted contained,
disjoint CSG subtraction is independently enforced. ROOT overlap check at
1e-5 mm reports zero overlaps. Random numbers are not used for construction.

Ten bounded straight ROOT rays check local depth and guard/gap paths. ECAL
fixture gives approximately0.574–0.583 X0; HCAL1.836–1.868 X0 along sampled
paths, including the respective absorber patches. Sensitive samples cross one
active element; deliberate face gaps cross none. These are unit-local paths,
not an IP eta scan or calorimeter performance. ROOT radiation/interaction
lengths derive from the exact native material mixtures.

DDSim fixture details and saved-hit checks are retained in
[transport.json](transport.json). Two seeded10 GeV mu- events exercise one ECAL
and one HCAL cassette with calorimeter readout. FTFP_BERT, seed42, zero field;
user particle handler disabled because this isolated compact has no tracker
region contract. No shower, optical response, digitization, thermal or mechanical
qualification is claimed. ACTS conversion is not applicable to this standalone
calorimeter hardware fixture.

Reproduce with [the tool guide](../../../tools/calorimeter_hardware/README.md).
Build/ROOT/event outputs remain ignored; publication figure uses existing
Matplotlib3.11.2 and was visually inspected. Historical execution failures and
remedies remain in the paired session journal; engineering assumptions remain
in [DES028](../../design/DES-028-calorimeter-cassettes.md).
