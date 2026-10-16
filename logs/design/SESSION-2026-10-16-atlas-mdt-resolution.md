# SESSION-2026-10-16-atlas-mdt-resolution

## Scope and evidence

Bounded follow-up to MUON-001, on codex/muon-reach-field-study at base
5b4e5d9e563505aea17e9b792458708c3175ec4a with existing prior study changes.
The user requested: "Make the MDT hit resolution match ATLAS".
Existing tracker, material and transport inputs were preserved.

## Decisions and outcomes

Use measured Run-2 single-tube sigma81.7um. Represent fitted stations with the
separately quoted ATLAS35um chamber coordinate and30um alignment benchmarks.
Their independent quadrature combination46.10um is an explicit inference;
81.7um is not added again to the fitted chamber precision. The measurement
coefficient becomes6.02635e-5p/B, the internal-MS crossover200.19GeV. Atlocal
100GeV,1% measurement precision needs0.603T; illustrative internal scattering
raises this to1.349T. Calorimeter reach estimates are unchanged.
The previous180um artifacts and review are retained in historical-180um.

## Assignments and checks

R1, explicit PhysVal/MuonTech generic-child mandate, read-only, base revision
above plus dirtyMUON-001files; owned files none; deliverable independent source,
formula and implementation closure. Primary ATLAS sources and arithmetic checked;
implementation closurePASS. Exact reviewed hashes and a subsequent coordinator
plot-label-only change are distinguished in review.json.

Regenerated results.json and PNG/SVG with existing NumPy/Matplotlib interpreter.
Built-in transport convergence/Highland/field controls passed. All20fieldcase
measurement terms scale by46.10/180; internal scattering and upstream transport
are unchanged. Project/session validators and git diff --check passed.
Full simulation/reconstruction remains outside this analytical update.

## Changed files

Calculation, report, result/plot artifacts, review, source catalogue locator,
TASK-B-MUONdisposition, historical snapshot and this session pair.
No production geometry or sign-off change. No commit/push/PR requested.

## Token accounting

Exact disjoint root/child per-turn client counters were not supplied. Usage
remains empty and unknown, not zero; no private client state accessed.
Session summary distinguishes existing observed project coverage from this gap.
