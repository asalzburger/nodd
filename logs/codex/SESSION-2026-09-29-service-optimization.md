# SESSION-2026-09-29-service-optimization — PR #25 follow-up

## Request and scope

The user asked to address more comments on PR #25. The expert
[comment](https://github.com/asalzburger/nodd/pull/25#issuecomment-5891018641)
requests moving first endcaps close to barrels with at least 10 mm clearance,
constant maximum service corridors, optional final-disc downstream extraction,
new module placements/mockups and hit-coverage/spacing optimization. Observed
head: `9b5b7f2aa14ad38434480c29666187aa893b73d3`.

Started `study/tracker-service-optimization` for the separate follow-up PR requested
by the user earlier. PR #24 remains unapproved. DES-011 records numerical choices
and review scope before implementation. Original DES-010 producers and retained
evidence are preserved. The four unrelated usage files remain untracked/untouched.

## Work in progress

Delegated independent routing/budget, module refill, path-gap metrics and mockup
work. The repeatable bounded study retains failure reasons and compares separate
coverage, spacing and area finalists. Selection uses training rays; dense final
validation includes a separate random seed and reports that cohort independently.

Initial inventory sizing shows 10 mm alone cannot host the original radial
barrel services. First-disc constraints therefore include the actual required
bay depth and body/support clearance. An optional last-disc bypass must occupy
separate space and feed the full downstream exit inventory. Full original module
restoration exceeds the 90 mm exit window at the chosen 1.1 capacity factor;
those failures remain visible rather than silently expanding the vessel gap.

## Environment and checks

Read the ACTS skill and sister checkout instructions. Preflight flags changed
setup/lock fingerprints. Warned the user, preserved existing sister changes at
HEAD `355ea68493b326956756c9386d2fd9eaf9328568`, and verified the installed pyvenv
with the existing step-size overlay, sensitivity binding, NumPy 2.5.3 and
Matplotlib 3.11.2. No shared dependency build/install or ACTS source edit.

An initial dashboard task state was invalid; corrected it to `active`.
Dashboard then validates 33 tasks, 12 documents and 13 review rounds. Initial
10 spacing controls pass; complete checks and execution provenance will follow.

## Usage

Exact client-reported counters for root and subagents are unavailable. Usage
remains empty; no historical totals are allocated to this bounded task and no
raw private client/model state is collected.


## Development probe and source freeze

The four-case limited search completed: primary plus ±10 mm barrel shifts and
original-pocket control all passed physical/service constraints. The primary
preserved all subsystem mean station counts and raised physical silicon from
177.303 to 196.510 m²; training mean stations rose 8.118 to 8.565. These are
**development-probe figures**, not final study results. Two shifted cases lowered
one subsystem mean and were excluded by the stated guard. The original-pocket
comparison is now retained as a control, excluded from primary compact-pocket
selection. No tuning uses the later validation sample.

Independent source audit added explicit unsupported-config/duplicate-ID guards,
null-statistic handling, baseline geometry validation, and final source/input
hash checks. Source is committed before the retained run. New source, tests,
configuration, DES-011 and tracking records form one isolated prototype.
