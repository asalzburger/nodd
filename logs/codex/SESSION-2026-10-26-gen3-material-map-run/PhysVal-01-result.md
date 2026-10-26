# GEN3RUN-PhysVal-01 independent result

Separate read-only PhysVal child01a177f4-e3e8-7e33-8531-4a40657d0883 reviewed
**2fff94bf5df903cff5cb8404754357ba318e71ef**,using the prepared explicit role
mandate. No edits,dependency changes,native physics rerun or human approval.
No blocking defect found in conservation,portal identity,binning or profile
normalization.

## Findings

Material locality is significant. Independent reduction of native mapped
`sur_distance` (midpoint-to-assigned-intersection distance,along the ray):

| Threshold | Steps | Mapped X0 fraction | Mapped L0 fraction |
| --- | ---: | ---: | ---: |
| >10mm | 6,732,954 | 80.2647% | 65.7231% |
| >50mm | 400,757 | 56.6015% | 39.6059% |
| >100mm | 133,137 | 37.6793% | 26.5982% |

Maximum413.289mm. These are diagnostic thresholds,not acceptance criteria.
Zero unmapped material does not imply local representation. They differ from
the original survey's shortest finite-portal distance.

P3:the configuration JSON validation block is descriptive;the validation CLI
has independent defaults and does not read that block. The actual campaign
used matching explicit flags,so its results are unaffected. Coordinator chose
the suggested documentation clarification instead of changing recorded steering
bytes:bin counts come from the manifest;generation settings come from CLIflags.

Before/after selects carrier placement only. Pinned ACTS
MaterialInteractionAssignment.cpp uses closest intersections without pre/post
matching. That limitation was correctly disclosed.

## Actual independent checks

- Regenerated52layer+14extra roles,65physical portals,15cylinders,50discs,8550bins.
  Verified both250/500 requests on the shared portal and500 resolution.
- Parsed compressed map:exact65keys/IDs/axes/grids,1672zero slabs,no unkeyed
  surface/volume material. Verified original/mapped/unmapped/validation ROOT hashes.
- Recomputed all100000ray identities and17137021steps;exact zero per-ray
  count/X0/L0 partition residuals.
- First100tracks/16977steps reproduce midpoint correction,unchanged lengths/
  material scales;max position discrepancy0.000122mm from float32 output rounding.
- Recomputed every validation profile,count,SEM and relative difference:
  maximum eta1.10036%X0/0.82810%L0,phi84.89495%/46.49846%.
- Matched all1417441validation material scales to their serialized bins using
  pinned ACTS float32 arithmetic. Ideal double lookup initially differed at
  boundaries;matching actual ACTS arithmetic resolved it.
- Eight pinned selection/profile controls and direct homogeneous1x1/multibin
  rejection controls passed. Source patch reversed to both exact authoritative
  full-run helper/C++ hashes;baseline/final sidecar hashes agree.
- Visually inspected pinned eta,phi andselected-portals PNGs;labels/readability
  correct and validation appears only as a total.

No geometry identity/seed separation is established for the original recording.
Phi1 removes real structure;SEM excludes map-training/systematic uncertainty.
Zero slabs cannot distinguish unsampled bins from sampled vacuum. No
material-order,displaced-origin,curved-track or tracking-performance validation.
Existing Spack fingerprint/source warnings remain;no fresh DD4hep/G4 execution
is claimed. The later coordinator locality table and P3 documentation fix are
response metadata outside the exact reviewed commit.
