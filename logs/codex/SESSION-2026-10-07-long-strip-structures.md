# SESSION-2026-10-07-long-strip-structures

Contemporaneous selected journal; one canonical owner for both barrel/endcap PRs.

## Selected user request

Develop long strips in separate barrel/endcap PRs. The cooled material between
sandwich sensors is the stave itself. Define mounting, quantify barrel anchors
against sag and define cable/cooling routes. Exploration is authorized; no design
approval or production integration is inferred.

## Barrel outcome and evidence

DES-022 DRAFT/PROTOTYPE, continuous5mm core/0.2mm CFRP skins between two separately
identified1D sensors.36 pairs/stave,86/108 staves at840/1060mm,40mrad relative
stereo,6.7/9.7mm separation. Source facts are pinned and classified; MIT sandwich
mechanics source added. Complete component load1.8004kg/stave, E70GPa/G5MPa/2g:
released-span minimum15 supports; recommend17 at163.75mm,25.95µm total gravity
bound, plus10µm joint allocation. Independent continuous Timoshenko10/20mm mesh
23.46µm. Moduli, joints, rings, torsion, thermal/dynamics remain unqualified.

Two nine-pair U circuits/half-stave, two12-pair harnesses and dimensioned6mm
LV/HV plus3.6mm48-fibre proposal. Fixed r1144..1169 services preserved.
Reference/adverse barrel packing pass for conductor-sized cable; gross CMS
comparator and warm LV return fail. First long disc must move to clear collector
ending1435mm; separate DES023 will retain the resulting coverage losses.

Native construction,13968 true1D sensors/unique face IDs and all material totals
passed: zero overlaps1e-5mm,105 material/navigation rays. Fresh ROOT persistence
passed; seeded DDSim saved8 positive-energy hits with full pairs in both layers.
77760 vacuum track sample agrees with independent planes on164 tracks; remaining
misses and rejected controls are retained. No ACTS conversion or calibrated hit
response was run. TDR-style SVG/PNG stave and anchor figures inspected.

## Failed attempts and corrections

Changed Spack fingerprints: preflight2, actual runtime imports/datasets verified.
Initial missing test file, factory naming/load path, strip field, flat ROOT voxel
bad_alloc, wrong-edge mounting4696overlaps and duplicate ring assembly names
were corrected. Export failed once on missing Path import and once on rounded
beam mesh endpoints; both fixed. Initial shear-dominance test used the wrong
span regime; the corrected short-span fixture retains inverse-G scaling.
Dashboard Status metadata corrected. Full receipts retain actual dirty a9d6367
execution/source hashes; later enclosing commits are not execution revisions.

## Accounting and remaining work

Endcap implementation and publication continue in this same bounded turn.
Usage remains empty: current-turn final counters are not available. No estimate,
partial import, duplicated owner or all-project total claim. Model/client version
and actual conversation boundaries remain unknown. No Slack/GitHub comment or
resource-recovery schedule was created. Earlier logs/science are preserved.
