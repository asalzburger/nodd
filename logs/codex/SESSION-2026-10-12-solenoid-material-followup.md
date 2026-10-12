# SESSION-2026-10-12-solenoid-material-followup

Bounded user request: add an estimate/plot of incremental pre-calorimeter
material t/X0 versus eta to PR64; add a high-level executive summary directly
to PR65. Start revision1bc3e39 on codex/tracker-solenoid-baseline, initially
clean apart from this new journal. Existing independent PRs retained.

Read the registered ATLAS solenoid sectionI/PDF1:45mm cold assembly0.66X0.
Read the primary PDG2024 Al radiation-length row8.897cm. These calibrate
explicit illustrative proxies; no new dependency, conductor recipe or vessel
wall design adopted. Reuse existing NumPy2.5.3/Matplotlib3.11.2 for plotting;
calculator itself uses the standard library. PDF skill used for source reading.

Model an annular cold assembly once, with assumed separate Al vessel walls/end
closures and thermal shells/end closures. Warm barrel walls end at closure
inner faces; positive-volume overlap rejection prevents joint double counts.
Analytic IP ray intervals include finite radial/axial clipping and the proposed
ECAL entrance envelope. Existing tracker/calorimeter and local services excluded.
Reference1.402108X0 centrally; sampled peak3.750593X0 at |eta|1.67. Lean/heavier
central1.002652/2.103163X0 are scenario spread, not statistical bounds.

Twelve controls pass, including six new independent cylinder/endcap/finite-edge/
joint/symmetry/ordering/rejection controls. An added NaN test initially had a
missing parenthesis and failed module import; fixed without changing criteria.
Initial plot footer overlapped its legend; corrected and final PNG/SVG inspected.
Actual input/code/profile/figure hashes and execution revision/dirty state retained.
No native DD4hep material scan or performance calculation claimed.

The PR65 description now starts with an executive summary covering hardware
already inherited, principal physical-description gaps and the cassette-to-sector
implementation sequence. Its code/head is unchanged; the summary is user-requested.
PR64 gets the material note, two figure formats and reproducible tools/data.
Project/source records updated; approval boundaries remain DRAFT.

Before this follow-up, PR64's1bc3e39 build and token-site checks passed after
the historical PR-order correction; the new material commit requires new CI.
Exact active-turn token counters unavailable. Usage remains empty (unknown),
with no allocation or duplication of shared client totals.

Local closeout: all12 controls, historical PR4 review test, project/session
validation, token-site build and link/artifact checks passed. Material figure
visually inspected. Both PRs target main; current design remains DRAFT.
Latest material-head hosted checks will be verified after push. Token summary
retains unknown current-turn coverage; no new usage observation invented.

Published material calculation/figure in5969102 and compact vector rendering
inad7dc05. Delivery evidence target `ad7dc0532a0405ca9b5ff49089fd25f305236ff2`; metadata-only closeout follows.
All2001 calculated samples remain retained; plotting keeps dense0.002 sampling
at the finite ends and thins smooth central/zero regions to reduce generated
SVG size. Final figures inspected and hashes checked. PR65 executive summary
verified through a subsequent body read.
