# SESSION-2026-09-18-tracker-first-layouts — First tracker subsystem and layer placement study with IdRes

## Scope and evidence

Contemporaneous record. Start revision `1c6409acd205c1caa7f76514e4994835d8425bf3`,
clean main; created branch `study/tracker-first-layouts`. PRs #11 and #12 were
already merged. Reconciled PR #11 merge metadata without changing sign-off.
Exact token usage, client version/thread ID and actual conversation start time
are unavailable. No private model state or upstream private source is stored.

## Selected conversation

User request (paraphrase): set the team to real tracker placement work, learn and
install IdRes, study the fixed coverage constraints, and make a PR with an
executive summary, two pages per proposal, strengths/weaknesses, priorities and
unresolved inputs. The assistant treated this as authorization for isolated
unsigned exploration, not production integration or human approval.

## Decisions and outcomes

SysArch coordinated the host/input contract, independent helix crossing/material
screen and consolidated review documents. TrackTech extracted public pinned ODD
placement references, proposed A/B and challenged component/service assumptions.
PhysVal independently calculated ray coverage and free transverse covariance and
audited IdRes. SoftEng installed the pinned tool and plotting environment,
exercised a supplied example, audited conventions and wrote the nODD adapter.
Role contributions are AI assistance, not human review.

A extends narrow pixel disks. B adds two disks per side and widens downstream
pixels, holding the barrel/strip layout fixed. Both retain pixels, strixels and
effective stereo long-strip stations. Proposed geometry/response/material values
are unsigned design choices. DES-001 stays a dependency, not a duplicated design.

Recommendation: A is the smaller resource control; B adds redundancy but does
not solve the short forward radial lever arm. Both have a three-pixel transition
weakness. B adds about 74% total ideal pixel area. At eta 4 from origin, nominal
3 T, its inverse-momentum precision improves slightly at high pT but worsens
about 7% at 1 GeV pT under the material scenario. Large inverse-momentum errors
must not be described as Gaussian fractional momentum resolution. Neither is
selected for production.

IdRes revision `d54d0e3c465cc0308becb737b04364ce5c68ce16` compiled unchanged
with GSL 2.8 and Apple clang 17. Ignored durable installation:
`reference/cache/idres`; plotting environment: `reference/cache/idres-venv`;
raw inputs/results: `reference/cache/idres-study`. Anonymous public distribution
and licensing remain unresolved; no source, examples or private endpoints are
committed. The analytic controls remain publicly runnable without IdRes.

## Commands and validation

The paired JSON records commands and results. The supplied IdRes example
produced 14 PNG/4 PDF files. An initial multi-field trial was wrong: all labelled
cases used the last 4 T field. Independent covariance exposed the discrepancy;
retained runs use one field per process. Exact zero material is unsafe upstream;
two positive near-zero scales test convergence. Raw strip hit reporting counts
each strip-classified surface twice, so raw hits and effective stations are
explicitly distinct. No upstream patch or tolerance relaxation was made.

Corrected execution: 22 runs, 729 expected finite rows each, 16,038 total with
none omitted. Independent checks cover 16 covariance comparisons, 486 station
counts and 162 material points. Hashes preserve inputs, code and result provenance.

Initial dashboard checks failed on a task role/workstream mismatch; corrected
the metadata. A dashboard build rejected PDF evidence under its text-only policy;
tracking now links the Markdown briefs containing PDF links. Corrected checks
pass without changing policies or tests.

Actually passed locally: 12 prototype tests, 25 dashboard/update-policy tests,
15 logging/documentation-link tests, 14 JavaScript assertions, dashboard
validation/build, 35 session records, seven retained hash links and whitespace
checks. Both PDFs have exactly two pages; the renderer rejects overflow and all
four pages were rendered and visually inspected. No ACTS module study,
DD4hep/Geant4, reconstruction efficiency or timing validation was performed.

## Changes and revision links

DES-006 executive summary, SI layer JSON, two Markdown/PDF briefs, role inputs,
drawings and three result reports. Added isolated study/IdRes/covariance/plot/brief
tools, synthetic tests and dependency pins. CI runs public prototype tests without
external IdRes access. Updated docs index, source catalogue, tracking and paired
session record. Exact paths are in the paired JSON. Publication revision is
recorded only after it exists; Git history locates this record's enclosing commit.

## Follow-up

Priority: agree physics/luminous criteria and small-radius/transition feasibility;
then module-aware ACTS coverage, component-informed material/support/services and
candidate ablations. Physical field maps, strip hardware, timing response and
full-simulation readiness remain named dependencies. Reviewers should assess
starting hypotheses and priorities, not grant final layout selection from ideal
surfaces. Formal approval remains human and exact-revision scoped. Final hosted
checks/publication are reported separately; no future CI pass or merge is inferred.
