# SESSION-2026-10-12-agent-workflow — Operational specialist workflow

## Scope and selected requests

The user asked whether nODD's documented roles were active agents, discussed
role profiles and reusable skills with agents started for bounded work, then
requested: “Prepare this infrastructure PR as suggested.” The agreed deliverable
includes eight role profiles, three reusable procedures, delegation rules,
assignment/handoff guidance and a documented pilot. It does not request continuous
background operation, external messages, detector changes or human sign-off.

The starting revision is `ed30e63fb0ab30b66d4084a9058906929006f792`, current
`origin/main` after fetch, on new branch `codex/agent-workflow`. The isolated
worktree started clean. The existing nODD checkout's unrelated changes were
preserved. The app worktree tool initially selected the parent workspace's Git
repository and could not resolve `origin/main`; a dedicated nODD Git worktree
was created instead. Initial sandboxed network/Git operations needed the
normal escalation path; their authorized retries succeeded.

## Implementation and decisions

- `.codex/agents/` contains ProRes, SysArch, TrackTech, CaloTech, MuonTech,
  SoftEng, PhysVal and PubDoc. Their names and mandates retain the existing
  [development plan](../../docs/DEVELOPMENT_PLAN.md#6-stage-b-agent-organization-and-responsibility-boundaries).
  Models, reasoning, permissions and concurrency are inherited rather than
  overridden. Profile existence is separate from live process activity.
- `.agents/skills/` contains `nodd-coordinate`, `nodd-design-evidence` and
  `nodd-review-validation`, with concise discovery metadata. Repository
  `AGENTS.md` requests bounded delegation for substantial subsystem, physical
  interface and scientific assessment work; small dependent work stays local.
- The standard-library [assignment helper](../../tools/agent_workflow/workflow.py)
  validates the nine-field contract and emits a full explicit-role prompt with
  source blob IDs, SHA-256 hashes and exact historical Git locators. It starts
  no process and changes no permissions. Tests cover behavioral ownership,
  unsafe paths and dirty files versus committed evidence.
- The [usage guide](../../docs/AGENT_WORKFLOW.md) describes discovery from the
  correct checkout, native profiles versus explicit role instructions, a runnable
  assignment example, handoffs, logging and review/approval boundaries.
- CI runs profile/skill validation and assignment tests. Current main retired
  the former progress dashboard on 2026-10-12; integration uses the current
  project-record checks and token-dashboard preview instead. Scientific task
  and review registers receive no infrastructure progress entries.

Two bounded implementation agents authored only the role profiles and helper
respectively (`/root/role_profiles`, `/root/workflow_tooling`). The coordinator
owns integration, skills, guidance, CI and the curated record. Their returned
checks were inspected, and the helper suite was independently run by the
coordinator. These are task identifiers, not permanent deployed role identities.

## Discovery and verification

The local executable reported `codex-cli 0.161.0`. A no-model
`codex debug prompt-input` diagnostic, filtered in memory, exposed the repository
instructions and all three skill descriptions in its Available skills catalogue.
An initial absolute-path heuristic missed the catalogue's aliased roots; actual
catalogue inspection confirmed discovery. No raw prompt was retained.

The skill-creator validator initially lacked PyYAML in both available Python
runtimes. PyYAML 6.0.3 was installed only in a temporary validation environment;
all three skills then passed its required checks. The repository helper itself
uses only Python 3.11+ standard-library modules and Git; CI uses Python 3.12.

The available desktop collaboration tool accepts a task name and message but
does not expose native profile selection. TOML validation establishes the
profile format; it does not verify native loading. The pilot therefore supplies
the complete role mandate through a saved prepared prompt and explicitly names
the working root and skill. Native profile loading remains unverified.

## Delegation pilot

The pilot reads the existing DES-020 short-strip barrel proposal and retained
evidence at `ed30e63fb0ab30b66d4084a9058906929006f792`. This assesses workflow
behavior, not new detector performance or design acceptance. Workflow profiles
and skills are the new uncommitted implementation in this PR; scientific input
bytes come from the fixed source commit. Assignments use `read-only` mode and
empty `writable_paths`. The coordinator retains their results; children own no
files and are instructed to make no further delegations or external mutations.

Assignments prepared with `workflow.py prepare`:

| Assignment | Child | Inputs and question |
| --- | --- | --- |
| `PILOT-2026-10-12-TrackTech` | `/root/pilot_tracktech` | DES-020, baseline-selection report, phi-tilted results: represented baseline, local services, handoffs and qualification questions. |
| `PILOT-2026-10-12-SysArch` | `/root/pilot_sysarch` | DES-020, DES-021, DES-010: physical interfaces and integration requirements/endpoint responsibilities. |
| `PILOT-2026-10-12-PhysVal` | `/root/pilot_physval` | DES-020, phi-tilted results and refined coverage JSON: supported claims, controls, uncertainty and missing scientific evidence. |

All deliverables are concise cited contributions with examined revision,
findings, actual checks and limitations. Completion means returning the bounded
answer or identifying missing evidence; it does not mean approving a design.

### Curated outcomes and reconciliation

TrackTech and SysArch ran in separate contexts in parallel. PhysVal was
subsequently dispatched with primary pinned inputs and no supplied specialist
conclusions. All three returned the exact source SHA, locators, actual checks,
limitations and no changed files. No child requested broader write ownership,
spawned another agent or claimed native profile loading/sign-off.

- TrackTech distinguished the represented +15° working baseline, occupied
  local services and material/route accounting from unqualified electronics,
  thermal, mechanical and service-connectivity claims. It verified all three
  dispatch source hashes, read governing context and checked the pinned compressed
  route ledger in memory. Its inherited-schedule conflict statement applies to
  the older first-disc schedule in DES-020.
- SysArch widened the interface source set at the same commit. DES-021 SE-I01
  already moves the first short-strip disc to 1335 mm and records 11.5 mm frame
  clearance from the collector. This reconciles the inherited schedule conflict
  reported by TrackTech; it does not establish installation or combined coverage.
  SysArch retained the recorded combined trunk capacity failure and bend/access
  gates. It verified source/dependency hashes, common route conventions and
  interface arithmetic. The [DES-025 integration contract](../../docs/design/DES-025-tracker-dd4hep-gen3.md)
  describes shared carrier/payload accounting rather than overlaying standalone
  service solids.
- PhysVal inspected primary coverage evidence before the narrative. It verified
  the three dispatch hashes and matched sample denominators, distinguished
  eligible layer-crossing counts from track efficiency and found that every
  retained refined mode still declares `passed:false`. It distinguished retained
  native and transport smoke evidence from reconstruction/response benchmarks.
  Historical dirty execution and amended source hashes prevent describing those
  artifacts as fresh execution at the examined publication SHA. It performed
  document/JSON/hash checks, not simulation or hardware qualification.

The coordinator retained two source-identity qualifications: DES-020 SB-C08's
50.90% collector mean fill differs from the selected tilted report's 51.54%; both
exceed the retained 50% screen. Also, the older collector/endcap conflict needs
reading with the later DES-021 placement amendment. PhysVal's limited barrel
source set does not override that broader interface assessment. No value,
criterion or design state was edited to resolve these statements. They remain
cited handoff information for future project work, not new formal review entries.

Additional sources were explicitly read at the same pinned commit: TrackTech
used DES-007/011, DES-010 services, ADR-006, manifest entries and the retained
layout; SysArch used DES-007/011/019/025, ADR-006, strip inputs and retained
reports; PhysVal used DES-007/011, DES-010 services, ADR-003 and retained
controls/coverage/native/transport/screening manifests. PhysVal read live issue
#20 only as current governance context. Public scientific references were not
freshly verified. Existing native/ROOT/Geant4/ACTS results were read, not rerun.

This observed pilot establishes role-conditioned dispatch, separate contexts,
pinned evidence, useful reconciliation and read-only behavior. It does not
establish native profile loading, independent human expertise or new scientific
acceptance. The coordinator verified no diff in scientific sources, detector
files, design/sign-off documents or project tracking/review registers.

### Reproducible assignments

The following curated contracts are the exact prepared inputs. Save one object
as an assignment JSON and run `workflow.py prepare`; each scientific source
revision is fixed. The workflow definitions used during dispatch are retained
in the implementation commit recorded in the paired JSON. Generated prompts
were temporary working artifacts, not client rollouts.

```json
[
  {
    "id": "PILOT-2026-10-12-TrackTech",
    "role": "TrackTech",
    "input_revision": "ed30e63fb0ab30b66d4084a9058906929006f792",
    "inputs": [
      "docs/design/DES-020-short-strip-barrel.md",
      "docs/validation/DES-020/baseline-selection.md",
      "docs/validation/DES-020/phi-tilted/results.md"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "task": "Prepare a bounded technical input on the selected short-strip barrel working baseline in DES-020. Identify what the represented geometry and local services establish, the subsystem handoffs and unresolved qualification questions. Use the pinned repository evidence; propose no new dimensions or design decisions.",
    "deliverable": "Return a concise cited role contribution to the coordinator for the existing infrastructure session journal. Include examined revision, findings, actual checks and limitations; do not write files.",
    "completion": "Resolve the bounded question from primary pinned sources or identify missing evidence. Return the contribution without sign-off, design edits or further delegation."
  },
  {
    "id": "PILOT-2026-10-12-SysArch",
    "role": "SysArch",
    "input_revision": "ed30e63fb0ab30b66d4084a9058906929006f792",
    "inputs": [
      "docs/design/DES-020-short-strip-barrel.md",
      "docs/design/DES-021-short-strip-endcap.md",
      "docs/design/DES-010-tracker-service-corridors.md"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "task": "Assess the physical interfaces of the DES-020 short-strip barrel working baseline with endcaps, pixel services and shared tracker allocations. Identify any integration requirements and endpoint responsibilities supported by the pinned source set. Make no geometry or design changes.",
    "deliverable": "Return a concise cited role contribution to the coordinator for the existing infrastructure session journal. Include examined revision, findings, actual checks and limitations; do not write files.",
    "completion": "Resolve the bounded question from primary pinned sources or identify missing evidence. Return the contribution without sign-off, design edits or further delegation."
  },
  {
    "id": "PILOT-2026-10-12-PhysVal",
    "role": "PhysVal",
    "input_revision": "ed30e63fb0ab30b66d4084a9058906929006f792",
    "inputs": [
      "docs/design/DES-020-short-strip-barrel.md",
      "docs/validation/DES-020/phi-tilted/results.md",
      "docs/validation/DES-020/phi-tilted/coverage-refined.json"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "task": "Assess which scientific or performance claims the pinned DES-020 short-strip barrel evidence supports. Identify validation coverage, controls, uncertainty and outstanding evidence needed for stronger claims. This is a document-based workflow pilot; do not rerun simulation or make design changes.",
    "deliverable": "Return a concise cited role contribution to the coordinator for the existing infrastructure session journal. Include examined revision, findings, actual checks and limitations; do not write files.",
    "completion": "Resolve the bounded question from primary pinned sources or identify missing evidence. Return the contribution without sign-off, design edits or further delegation."
  }
]
```


## Checks and accounting

The paired JSON retains actual check results. Workflow validation and 14 helper
tests passed, all three skill-creator checks passed, and the token-dashboard
preview built successfully. Session validation covered 169 pairs; scientific
record validation covered 60 tasks, 32 documents and 19 review rounds.
All 28 project-record, 33 session-logging and 10 token-dashboard Python tests
also passed (85 Python tests including the 14 helper tests). Token-chart keyboard
and mode checks passed in the bundled Node runtime. Local guidance/journal links
and headings, the existing infrastructure PR classification gate, and unchanged
scientific sources were checked. Final PR metadata will be recorded at closeout.

Exact per-turn counters and stable desktop thread/turn IDs are not exposed for
this task or its children. `usage` is empty; this does not mean zero usage. The
journal summary reports historical observed coverage (117/169 sessions and 209
retained turns at this point); no estimated or overlapping child usage is added. Observed historical input
and output sums are 617,282,110 and 3,530,717 tokens respectively; these are
retained project totals, not measurements of this task.
No actual execution model is inferred from a configured default.

No detector parameters, DES/ADR lifecycle states, human sign-off records or
scientific provenance are changed. DES-020/DES-021/DES-010 are read-only pilot
inputs; ADR-004 supplies the existing logging policy. Official Codex profile and
skill-discovery references, accessed 2026-10-12, are linked from the usage guide.
