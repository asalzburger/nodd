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


Source freeze: `6c882257c368927732315dbc756f1b89263d95af`. The retained run reports
clean tracked source and snapshots all inputs. All 33 new tests passed in
4.420 s. The full module suite ran 123 tests in 60.816 s: 120 passed and three
native tests were skipped in system Python. Native finalist checks run separately
inside the verified ACTS runtime. All 32 logging tests passed in 1.198 s. SHA-256
checks confirm all 21 original DES-010 artifacts remain byte-identical.

## Rejected first run and corrective protocol

The complete frozen-source run produced111 candidates,39 geometry/capacity
passes and23 mean-hit guard passes. All five retained cases completed36192
mode-track evaluations and48 native checks each with zero mismatches. The22
PNG/PDF figures rendered; all source/input hashes remained unchanged.

Post-run local coverage inspection exposed a failure hidden by the mean score:
24 long-strip barrel rows leave a15.3167mm stereo-projected active seam atz=0.
All96 eta=0/zvertex=0 rays per mode lost both long-strip stations, while PR25
retained means2/2/1.9375 (straight/positive/negative). Native samples contained
no eta=0 rays; their agreement was not coverage acceptance. The first full run,
figures and exact central-cohort diagnostic are retained under
`docs/validation/DES-011-optimization-rejected-even-rows/`.

Before the corrective run, DES-011 adds half-length1300mm (23rows, central row,
12/11 modules per signed half-stave), strict central mean/zero-hit guards and
no newly completely blind eta/vertex strata. Smaller local regressions remain
reported. Sensor shapes, no-z-stagger long-strip policy and harness architecture
are unchanged. Explicit central native probes are added. First-run dense grids
now serve regression testing; a fresh random seed202609293 is independent.
Independent agents confirmed the1300 alternatives fit unchanged service limits.
The earlier27 dashboard tests passed in178.741s; logging32 tests also passed.

The new local guard correctly rejected the first1300 development seed: at
straight eta=-0.5,vertexz=+150mm both unchanged-radius LS layers shared a row seam.
The existing±10mm intermediate-radius exploration can decorrelate those seams.
Its seed now requires physical/mean/central constraints, while all final ranking
roles still require the full local guard. This search-stage distinction is
explicit in DES-011; a seed is never presented as a validated finalist.

The explicit1300/front-loaded/p190/s680 probe completed with the+10mm variant
passing all final training guards, service/body/host checks. A fourth declared
length1287.3333333333333mm preserves the retained PR25 barrel-row pitch exactly:
(22×((2800−96)/24)+96)/2. This provides a physical baseline-preserving alternative
to stretching23rows. The full revised configuration has216 primary cases plus
the bounded radius/pocket follow-up. No new longitudinal staggering is introduced.

Revised source freeze: `10203d9a3f41d82cb467a7deb75e8293b0f1cc95`.
The canonical corrected run started with clean tracked source and records all
input/source hashes. Full revised tests:131 run in64.478s,128pass and3ACTS skips
in systemPython; finalist native audits run separately in the verified runtime.

## Second run: coverage passes, individual-component fit fails

The219-case revised study completed with clean source/input hash checks:
111geometry/aggregate-capacity passes,81mean guards and33fulltrainingguards.
All five retained cases completed dense validation and72native tracks each
(360total), all passed. An independent audit confirmed exact local-guard results
and preserved smaller local losses. The original DES01021artifact hashes remain
unchanged; an initial recheck helper used the wrong manifestkey and was corrected.

Independent service audit then found the compact strips pockets cannot contain
the budget's13.4mm power cable plus2mm boundary skins (17.4mm necessarytotal,
rounded18). The12mm return pipe also fails10/15mm passages. Aggregatearea and
sensitive ACTS checks did not catch this dimensional mismatch. Preserve this
run under`docs/validation/DES-011-optimization-rejected-pocket-depths/`; original
larger-pocket control is assessed separately. DES-011 adds explicit route/throat
individualitem bounds and an eight-primary-case followup with freshseed202609294.
This is a scoped correction, not a claim the earlier216case scan passed the newgate.

Final service-source freeze: `ac61f766b34f9bb60748e8fc4258a41037ca1e33`.
The bounded followup starts with clean tracked source. All11candidate geometries
pass aggregate capacity and the new necessary individualcomponent fit gates;
training roles remain unchanged. Fullmodule suite136tests in64.174s:133pass,
3ACTS-dependent skips; actualselectedcase ACTS jobs run separately. Compressed
retained second-study JSON decodes to the exact originalhashed bytes; all219
records are retained. Finaldense/native outcomes follow after completion.

The user additionally requested: “Push the summary to the PR when done.”
The final numerical outcome, routing views, limitations and separate follow-up
PR link will be posted to PR #25 after validation completes.

## Final executed outcome

All 11 corrected candidates pass geometry/reference-area/known round-component
checks. Five retained layouts completed 180,960 mode-track evaluations and 360
native ACTS trajectories with zero mismatches (maximum residual2.048e-7mm).
Source/input hashes remained unchanged. Coverage, area and original-pocket cases
pass dense coverage gates. The spacing candidate loses17 straight long-strip
station opportunities (10984→10967/12064rays), fails the frozen mean guard and
is withheld. Smaller local regressions remain explicit; no holdout reranking.

The coverage case yields9.0758 mean stations and196.473m² versus baseline8.2284
and177.303m², but adds local zero-hit rays. The original-pocket control yields
9.0182 and197.250m² without increased zero-hit fractions in measured bins; it is
a comparison option for engineering review, not an approved default. Known
stripitem allowance leaves only0.6mm extra beyond cable13.4mm+two2mm skins;
bends, connectors and ancillary shapes remain unqualified. Adversecapacitiesfail.

An independent paired training audit finds last-disc bypass saves2/3/2mm trunk
width, no silicon area, and0.01582 mean stations. This marginal gain argues for
keeping the topology optional. Twenty-two final PNG/PDF views rendered and
routing/transverse/comparison figures were inspected. The spacing failure is
marked in the figure. Gzip study encoding preserves exactoriginalbytes/hashes.

Publication checks and the PR25 reply link will be added after posting. A small
tracking-update helper initially addressed the wrong reviews key; corrected
`rounds` without modifying review approval state. No exact usage counters were
exposed; usage remains empty. Unrelated usage-summary files remain untouched.

## Publication and bounded-task closeout

Published [draft PR #28](https://github.com/asalzburger/nodd/pull/28), stacked on PR #25, at
`770d6b6fe203cd79be6111188aff8ebffd022efd`. The GitHub dashboard build passed; PR deployment
was skipped. Posted the [requested summary on PR #25](https://github.com/asalzburger/nodd/pull/25#issuecomment-5898939972), including outcomes, failed candidates, local losses, engineering
limits and the repeatable workflow. Expert acceptance remains unrecorded.

A server interruption occurred after PR creation. Checked remote comments before
retrying: the summary had not been posted, so it was published once. Initial
sandbox push failed DNS resolution; approved network execution succeeded.

The completed task is the bounded prototype and review handoff. DES-011 remains
DRAFT, PR #24 remains an unapproved working hypothesis, and no review condition
is marked resolved by automation. Publication metadata is a later snapshot than
the numerical producer revision. Exact usage counters remain unavailable for
this task; historical project totals must not be attributed to this session.

Final publication checks passed: 60 local paired session records; dashboard
validation (33 tasks, 12 documents, 13 review rounds) and build; whitespace check.
Session summary reports historical observed input 134,594,309 and output 674,111
across 79 turns in 42/60 sessions. These exclude unobserved usage for this task
and are not a complete project total.
