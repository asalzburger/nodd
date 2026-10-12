# SESSION-2026-10-12-solenoid-baseline — magnet baseline

Status: in progress; DRAFT deliverables on dedicated `codex/tracker-solenoid-baseline`.
Starting main: `da5c469f4d64a711c4f466cac79ff51e83244859`. Both new worktrees were clean;
unrelated primary-checkout changes were preserved. Companion task has its own
paired record; shared client usage is not allocated by guesswork.

## User-visible request and correction

User requested two PRs: an ATLAS-style central3T solenoid around the tracker
with sufficient space and an R–Z view; and a detailed ODD/nODD calorimeter
hardware assessment covering support, cryostat, powering and related services,
with performance/software updates deferred. PR8 proved to concern pixels; the
user confirmed PR6 as the intended magnet reference.

## Work and evidence

Six physical/interface controls passed; 143.173758 MJ and 1.558656 m vessel radius; 69 tracker source/input hashes matched, 45,646 sensors plotted; final PNG/SVG visually inspected.

Relevant DES: DES-026. Proposal, independent numerical/static controls,
source catalogue and scientific project record updated. The magnet uses only
the PR6 energy kernel at d2437a7, not the whole alternate-layout branch.
The calorimeter assessment distinguishes maintained beam-pipe/tracker assembly,
ODD inherited stacks and proposed hardware. No new dependency was installed,
no detector production geometry changed, and no human approval inferred.

PDF skill: registered ATLAS solenoid and ATLAS/CMS hardware passages read with
bundled pypdf. Existing envelope plotting environment supplies NumPy2.5.3 and
Matplotlib3.11.2. System/bundled Python lacked Matplotlib; existing environment
resolved this without installation. Local PDF hashes match catalogue. CDS web
challenge blocked retrieval; existing registered copies were used.

Inspection corrections retained: initial guessed DES003/ODD envelope filenames
and schema role key were absent and replaced with actual file/key inventory.
Sensor inventory uses `role=sensitive`, not a boolean sensitive field. The
first R–Z header overlapped its legend and was corrected after visual review.
The initial hand-written copper subtotal was corrected to238.198g/cm² from the
computed inventory. Shell network access to the public source initially failed;
the authorized read-only GitHub API retry succeeded with sandbox escalation.
No scientific test failed; none of these inspection errors are passing checks.

## Token coverage

Exact active-turn counters unavailable. `usage` remains empty. Observed sums
for this session are unknown; historical project coverage remains partial.
No estimate, cumulative thread total, or duplicated observation is entered.

## Commands and final delivery

Key commands: PR6 exact Git source reads; public source/PDF hash verification;
`python -B tools/solenoid_baseline/run.py`;
`python -B -m unittest discover -s tools/solenoid_baseline -p 'test_*.py' -v`.
Repository/logging/site checks and actual commit/PR metadata follow at closeout.

Final local checks passed: project records, paired session records, token-site
build, subsystem controls, document links, artifact hashes and whitespace.
No native detector execution is claimed for these draft/static changes.

The initial working-tree whitespace check omitted untracked files. Staging
revealed trailing spaces in Matplotlib SVG paths. The renderer now strips
trailing spaces and pins SVG hash IDs/date metadata before output hashing.
A normal correction commit precedes publication; no shared history rewritten.
