# SESSION-2026-10-12-calorimeter-assemblies — Sector and complete assemblies

2026-10-12, contemporaneous bounded follow-up to PR67. Starting parent9b409b7
on codex/calorimeter-assemblies; actual complete native execution hashes and
revision are retained separately. Primary user's unrelated checkout untouched.
No new human approval or scientific sign-off inferred.

User request (selected paraphrase): after designing the two representative
cassettes, build sectors and complete barrel/endcap assemblies with reproducible
geometry, mass and material checks. Technology confirmation stays Si-W ECAL and
steel/scintillator HCAL. DES029 was drafted before this assembly implementation.

One reusable cassette/sector factory now builds16 sectors per barrel and both
endcaps. Unit-fixture absorber patches are excluded; full plates, edge frames,
back covers, barrel end flanges and endcap aperture/rim frames have separate
ownership. Proper mirrored-end rotations, zero-based IDs, deterministic packing,
central inputs and fixture rail ports/flush pipe ends are explicit.

No new software installed. Existing verified Spack DD4hep1.38/ROOT6.40.04/
Geant4 11.4.2 runtime reused. Native capacity audit's initial Xtru GetX/Y call
used the wrong API; fixed indexed access before rerun.14 physical/negative
controls pass. Full native audit checks every logical placement and physical
replica, scales actual shared capacities to127680 cassettes, checks bounded ID
fields and384 native round trips, and computes57 ROOT material rays. Complete
ROOT overlap check actually ran:39,576,444 candidates, zero overlaps at10 nm;
checking418.774 s. Modified cassette units separately pass all1168 cell checks,
constituent agreement and overlaps. Exact source/config/compact/library and ROOT
artifact hashes accompany evidence; ignored placement/event files reproducible.

Uniform endcap packing exposes poor active area: ECAL31.9%, HCAL38.8%; sampled
high-eta rays can cross absorber without sensors. Geometry correctness is not
acceptance. Continuous heat sums469.27 kW with22.45 kg/s ideal water flow; PCB/
package/power hypotheses and full service architecture remain under review.
No geometry tuned to conceal these results. Smaller/shaped edge/aperture modules
and service/structural qualification are concrete follow-ups.

Full-sector DDSim conversion succeeded but two oversized fixture jobs remained
in initialization for several minutes; task-owned processes stopped, startup
logs retained locally. An explicitly sparse fixture keeps all plates/frames and
one selected cassette per layer at sector0, barrel and both endcap sides. Saved
seeded muon hit audit is distinct from full native geometry validation; full
Geant4 detector transport and realistic calorimeter response remain open.

PR67 hosted CI initially failed because synthetic project-record fixtures
omitted prototypes/. Copy corrected without relaxing checks; all28 record
controls passed. Correction b725f43 pushed to the parent PR using ordinary
history while preserving this uncommitted assembly work. Its hosted build and
token-site checks subsequently passed. Parent metadata updated from actual SHA.

Paired JSON retains actual checks and changed files. Exact client turn token
counters remain unavailable; usage empty/unknown. No counters copied, estimated,
divided or duplicated with the preceding cassette record. Session summary and
site build preserve existing observed totals and missing coverage.

All three final sparse DDSim events completed; saved-hit parent IDs, cell ranges
and positive energies passed the independent ROOT reader. Exact fixture/source/
root/log hashes are retained in DES029 transport evidence.
