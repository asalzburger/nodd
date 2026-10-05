# SESSION-2026-10-05-issue38-radial-revision — Radial disc module revision

The user rejected the earlier global x/y-aligned proposal because module axes should retain a stable relation to transverse and longitudinal resolution, particularly for non-square pixels. They requested concentric arrangements of single, optionally double and quad modules, retaining the innermost ring, and allowed 15–20% overlap where needed for hermeticity. This revision interprets 15% as preferred and 20% as the hard ceiling, while retaining coverage and physical-body checks.

PR41 branch was clean at bab2357e99ba4a7e5623b8362174b94e16ef2545. The original Cartesian figures and evidence remain retained; revised evidence goes under radial-revision/. PR40 positioning and production geometry are unchanged. Updated the DRAFT design contract before searching.

The acts-spack preflight found changed setup/lock fingerprints; reverified actual environment: DD4hep1.38, Geant411.4.2 and installed acts-nodd Python with NumPy2.5.3, Shapely2.1.2, Matplotlib3.11.2 and sensitivity assignment. No shared dependencies or ACTS source are changed.

Current-turn tokens are unknown until closure and are not estimated. Prior recovered turns keep their existing canonical owners. This bounded revision has its own resource record.

The current scientific revision turn is `01a10d0d-89a2-74f3-ab78-cbf70a5057ab`, started 2026-10-05T17:12:33Z, and remains active. Usage-only recovery identified it without importing partial counts; actual execution model/client version remain null.

Scanned36 ring/family candidates. Selected359 singles in9 radial rings; first-disc whole overlap15.593%, annular17.478%, maximum across distances19.483%. Positive continuous straight-ray certificates and reflected negative geometry pass;0.2mm occupied-body separation is retained. Larger-family controls keep0.2mm inactive seams and fail gaps/overlap; no universal mixed-family infeasibility claim. Rectangular25×100µm test covariance is stable at module centres;17.435degree corner departures remain, especially in the retained inner ring. No fitted track-resolution claim.

Sixteen geometry/axis controls passed. Initial native audit stopped because exact set comparison split reflected source datums differing by4.55e-13mm. Added an explicit1e-9mm pairing tolerance and a changed-position rejection control; actual native datums and physical limits remain unchanged. Rerun constructed6462 candidate and8064 baseline planes:324 matched tracks each and6 exhaustive controls passed, with zero target-disc misses and no native/analytic mismatches.

Retained new comparison/covariance figures and inspected the PNGs. Original Cartesian evidence is unchanged. Guard0.1mm remains conditional;0.5mm control fails. Body radius202.035mm and all inherited shared-service packing scenarios need engineering revision; no acceptance/lifecycle promotion.

Local closeout checks passed:99 paired logs,79 existing observed turns in42 sessions and57 sessions without usage;41 dashboard tasks,22 documents,19 review rounds;31 dashboard/document tests, ignored build, retained artifact/producer hashes and full base-relative whitespace checks. These are observed partial accounting totals, not all-project coverage. Current revision usage remains empty until client closure.
