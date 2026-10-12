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
| `PILOT-2026-10-12-PhysVal` | Pending dispatch | DES-020, phi-tilted results and refined coverage JSON: supported claims, controls, uncertainty and missing scientific evidence. |

All deliverables are concise cited contributions with examined revision,
findings, actual checks and limitations. Completion means returning the bounded
answer or identifying missing evidence; it does not mean approving a design.

Pilot results and final closeout are still being collected.

## Checks and accounting

The paired JSON retains actual check results. Workflow validation and 14 helper
tests passed, all three skill-creator checks passed, and the token-dashboard
preview built successfully. Session validation covered 169 pairs; scientific
record validation covered 60 tasks, 32 documents and 19 review rounds.
Broader relevant checks and final PR metadata will be recorded at closeout.

Exact per-turn counters and stable desktop thread/turn IDs are not exposed for
this task or its children. `usage` is empty; this does not mean zero usage. The
journal summary reports historical observed coverage (117/169 sessions and 209
retained turns at this point); no estimated or overlapping child usage is added.
No actual execution model is inferred from a configured default.

No detector parameters, DES/ADR lifecycle states, human sign-off records or
scientific provenance are changed. DES-020/DES-021/DES-010 are read-only pilot
inputs; ADR-004 supplies the existing logging policy. Official Codex profile and
skill-discovery references, accessed 2026-10-12, are linked from the usage guide.
