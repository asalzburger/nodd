# SESSION-2026-11-18-lar-compact-hadron-prototype

## Scope and evidence

Contemporaneous user-authorized isolated redesign from main
f3ece1d6a6816c8172dfa841d63e5424730e8228, branch codex/lar-compact-hadron-prototype.
No initial worktree changes; unrelated workspace clones/worktrees preserved.
No maintained layout, tracker/solenoid source or human approval state changed.

## Selected conversation

User requested a LAr prototype fitting the tracker+solenoid, respecting vessel,
vacuum and bath needs, enough X0 for the14TeV hadron option, retained ALLEGRO
inclination/relative sampling radii and repeated10k electron controls. Prior
12-worker setting, exact10–80GeV/flatη−3…3/fullφ sample and SVG retention persist.
Assistant treats this as an unsigned PROTOTYPE exploration, separates native
sampling from walls/services and will report actual raw-width precision bounds.

## Decisions and outcomes

The lower warm bore follows1640mm assembly+60mm interface; front vacuum/wall/bath
budgets remain explicit. Scientific input, native material-depth gates and
prospective paired statistics precede event response analysis. Claims remain
limited to represented geometry and raw active deposits; no human design or
engineering acceptance is inferred from simulations or agent assessment.

## Token accounting

Current parent turn is active and excluded. Exact closed specialist turn usage
will be imported only after strict usage-only reconciliation and explicit app
turn/assignment match. Models/client versions remain unknown where unexposed.
No estimated usage, inherited prefix allocation or private reasoning is retained.

## Specialist assignments

Main uses nodd-coordinate, nodd-design-evidence and nodd-review-validation; generic children receive complete prepared role instructions, not native profile selection.

LAR-COMPACT-CALOTECH-DESIGN; CaloTech; exact f3ece1d6a6816c8172dfa841d63e5424730e8228; read-only/owned files none; inputs docs/design/DES-026-tracker-solenoid-baseline.md, docs/design/DES-032-allegro-lar-barrel.md, docs/design/DES-033-allegro-lar-endcaps.md, tools/lar_calorimeter/barrel.json, tools/lar_calorimeter/barrel_geometry.py, tools/lar_calorimeter/endcaps.json, tools/lar_calorimeter/services.json, docs/validation/lar10k/protocol.md. Task: Derive feasible compact LAr ECAL around DES026 with real vacuum/bath/walls, enough sampling X0 for 14 TeV pp, retaining 50.18deg inclination and relative sampling radii. Provisionally preserve Rout/Rin and normalized compartment boundaries, never uniformly shrink physical plate/gap thickness. Calculate integer planes, lead thickness and gaps preserving sampling precision if feasible. Quantify X0 for barrel and coherent endcap and identify tradeoffs. Primary public LHC/FCC depth sources needed; distinguish 14TeV pp from FCC-hh and low-energy control scope. Propose a quantitative configuration BEFORE transport. Exact source read-only; standard-library calculation/import okay, no native runtime, source writes, event transport, installation, publication or further delegation. Deliverable: Quantitative candidate parameter options, formulas and X0 target rationale with source locators, constraints and remaining gates.

LAR-COMPACT-SYSARCH-ENVELOPE; SysArch; exact f3ece1d6a6816c8172dfa841d63e5424730e8228; read-only/owned files none; inputs docs/design/DES-026-tracker-solenoid-baseline.md, docs/design/DES-032-allegro-lar-barrel.md, docs/design/DES-033-allegro-lar-endcaps.md, tools/lar_calorimeter/barrel.json, tools/lar_calorimeter/barrel_geometry.py, tools/lar_calorimeter/endcaps.json, tools/lar_calorimeter/services.json, docs/validation/lar10k/protocol.md. Task: Assess exact DES026 tracker+solenoid surfaces, reservations and clearances for a compact LAr prototype. Recommend smallest defensible warm bore/sampling front while retaining conservative vessel/wall, vacuum, bath and service budgets. Inspect endcap/HCAL/forward handovers and existing side/rear routing proposals. Do not silently shrink services or certify model wall equivalents as pressure-vessel qualification. User authorizes isolated prototype; maintained baseline unchanged. Read-only, no native runtime, writes, transport, installation, publication or further delegation. Deliverable: Exact baseline envelope numbers, proposed radial/axial ledger and service implications, source locators and explicit engineering unknowns.

LAR-COMPACT-PHYSVAL-PROTOCOL; PhysVal; exact f3ece1d6a6816c8172dfa841d63e5424730e8228; read-only/ownedfiles none; inputs prior protocol/summary/README and transport/compare.py; prospective matched 10k inference and depth/claim requirements; no runtime, writes, publication, private accounting or delegation. Exact candidate review later.

LAR-COMPACT-SOFTENG-PAIR-ANALYSIS; SoftEng; exact f3ece1d6a6816c8172dfa841d63e5424730e8228; writeonlycompact_compare.py/test_compact_compare.py; priorprotocol/code/summaryinput; pairedLAranalysisandplotsperprospectivePhysVal; no runtime/transport/publication/delegation.

## Design and prospective validation outcome

CaloTech and SysArch returned bounded read-only quantitative proposals at f3ece1d6.
PhysVal supplied prospective paired-width criteria, zeros/tails, energy×region
controls and transition migration; no invented noninferiority margin. Main froze
1408plane/2.6mmPb/1.2mmPCB barrel at1772.8–2103.649779mm, old inclination and
relative radii;210mm rearbath/3banks/10columns;600mm deep endcaps preserving
internal materials/radii/inclination and rearbath. Warmbore1700mm retains1640+60
tracker/magnet reservation. External1000mmfront routing uses400mm actual bends.
All changes remain opt-in isolated prototype; pressure/thermal/radiation/pileup
and full collider qualification remain open.

Actual native construction, shape/mass/readout and combined overlap checks pass
with0overlaps. First barrel audit exposed hardcoded lastplane1534/1535; replaced
by exact candidate last-pair indices, retaining same boundary checks. Native
sampling scan finds barrel phase minimum25.61565X0 and endcap selectedcore
minimum27.90662X0; walls/baths/services excluded. Original selected minima are
20.74831/21.10139X0. Finite-grid material evidence is not an all-direction bound.

Initial serial24 failed before events because tracker+ECAL composer lacked global
world Vacuum/Air definitions when no tracker was supplied; isolatedECAL composer
corrected this. Second startup failed because explicit library-only CMake targets
omit .components catalogs; built the two existing Components targets. Failed
pilot directories retained and excluded. Component geometry/material XML remained
byte-identical across the world-composition correction. Runtime imports/Geant4
11.4.3 datasets verified after preflight setup/lock warning; ROOT6.40.04. Noinstall.

SoftEng wrote only compact_compare.py/test_compact_compare.py under explicit role
assignment; seven tests and synthetic-only11figuregroup smoke/visual checks pass.
Main adds exact candidate native-count gate instead of old43648constant: expected
40832 comes independently from compact readout tables and native inventories.

LAR-COMPACT-PHYSVAL-CANDIDATE; PhysVal; exact b88931080ce5d376f9e2ee5fc597786f812d3fd6; read-only/ownedfilesnone; source setpreparedcontract above and ignoredactualnativeevidence; scientific/source fidelity/prospective pairing assessment before10k; no runtime/writes/transport/delegation.

Before anyproductionresponseanalysis: finer nativeangulargrid600mmendcap min24.389619X0 atη2.7/φ1.179097rad, a support-bandshortfall missedbyselectedcoreangles. Main increasesendcapdepth600→650mm retainingrear250bath, allmaterials/radii/inclination. Warmback6260/HCALfront6760. This native-materialrequirementrefinement precedes anyRstatistics; prior600mmcontrols/evidence remain labelledseparate. Fullnewnative/material/transportcontrols required.

## Exact candidate review and remedies

PhysVal reviewed b88931080ce5d376f9e2ee5fc597786f812d3fd6 read-only: prospective
paired response criteria sound; found external materials hash binding missing,
48globalphi endcap probes aliasing electrode phase, and confirmed600mm depth
shortfall24.389619X0 atη2.7. SoftEng added frozen materials hashes plus negative
tests (8tests pass). Main added32 actual within-period probes for each of the
four native period counts at every0.05η step. New650mm native scan has9088rays,
minimum25.613359X0 atη0; old reference minimum0.081382X0 atη1.35. These are finite
probe minima, not a proof of the continuous minimum or high-energy containment.
Newendcap/combinedshape+overlap audits pass0overlaps. Stale600mm unit expectation
failed after the explicit depth amendment; test updated to650/retained250bath,
not weakened.28analysis tests plus2compactbudget tests pass. Maintained default
barrelXML/materials regenerate byte-identically to cleanf3 exports.

600mmserial/MT24control passes15962exactcanonicalhits and allprimary/cellreadbacks;
650mmcontrols are separate, rerun before production. No600mmresponse statistics
were inspected or used for design selection. Final650mm uses6260warmback and
6760design-onlyHCALfront; source branch remains isolated.

LAR-COMPACT-PHYSVAL-650-FROZEN; PhysVal; exact afc79974ea5c407ee571048fdb71a155e2bfa87a;read-only/ownedfilesnone; final650source/protocol/contract/nativecompactsummary and actualignored9088ray/component/union evidence; check all earlierremedies before/finalcharacterization; no runtime/writes/privateaccounting/publication/delegation.

## Frozen650review and production start

PhysVal independently assessed afc79974ea5c407ee571048fdb71a155e2bfa87a read-only:
material hash and actual-period sweep findings remedied;9088rayminimum25.613359
andη2.7minimum26.835508 verified,650depth/250rear/6260warmback,27sourcehashes,
production/native XML identity and2196aggregatevalues checked. No material issue
blocking characterization after controls. No independent native rerun or human
acceptance. P3stale6210text corrected to6260 in the final design note.

Final650controls pass:24serial/MTevents and15584exactcanonicalhits; native-limit
and5mm100event pilots plus all-primary/cellreadbacks. The full10k production
started with12workers, unchangedFTFP_BERT/cuts/step/eventseed and30GiB reserve.
About149GiB was free; no sample trimming/deletion. Production-model sourceafc;
physical compact/material/primary hashes equal the prospective frozencontract.
Defaultscientificgeometry and originalreference samples are preserved.

Closed specialist usage recovery selects six exactly matched turns only:
110requests,21,019,409input+73,949output=21,093,358tokens. Cached/reasoning are
subsets. Activeparent/650review-atcapture and future result turns excluded.
Strict cumulative/request deltas and parent-childmetadata checked; no private
reasoning, raw app responses or historical counter duplication retained.

## Draft publication and synchronized records

Draft PR148 opened with the reviewed source, native plots and explicit pending
10k result. Connector writes return integration403; authenticated gh fallback
succeeded. This is not an automatic approval rejection. Existing labels
campaign:calorimeters,scope:baseline-design,enhancement applied; nonexistent
prototype label was not created. Current task tracking, inventory links and
seven exact closed specialist turns are synchronized to PR148. Visible-source
curation retains only actual started child relationships, not completed/interacted
notifications that initially triggered the conflicting-parent guard. No counters
or validation rules changed to remedy that curation error.

Observed seven-turn usage:122requests,23,381,088input+82,018output=23,463,106tokens;
Cached input23,022,080 and reasoning39,997 are subsets. Current
parent remains active/unaccounted. Full paired validation/source hashes are the
canonical evidence; no main merge or human sign-off.
