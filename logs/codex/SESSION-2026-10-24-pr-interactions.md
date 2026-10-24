# SESSION-2026-10-24-pr-interactions — Per-PR interaction provenance

## Scope

Infrastructure work starting from main
`fbf81c4c72469c1bda0cd6122f9912af6f17228d` in the isolated
`codex/pr-interaction-ledger` worktree. Existing nODD worktrees and their local
changes are preserved. ADR-004 governs curated evidence and token ownership;
its DRAFT status is unchanged. No scientific progress or sign-off is created.

## Selected conversation

User request, exact:

> A new infrastructure PR:
>
> - add a new directory “interactions”, where you add for every single PR the human action(everyone else than the GitHub ‘asalzburger’ account and all the prompt inputs, and codex remote inputs) and the reactions (responses and model and agent reactions)
> - identify the type of interaction (comment, issue, prompt, upload)
> - name the parties
> - isolate the corresponding token account
> - name he agent and subagent roles
> - list tools that had operated:
> —- as native codex tools
> —- as tools installed by codex itself
> —- as tools provided through software installed per instruction (idres, spack externals, acts, unrooted)
> - make individual files to avoid merge conflicts
> - make a rule to keep this in synch when the token accounting per PR is done

Assistant outcome: separate records for every existing PR, with retained public
actions/reactions, matched visible messages, roles/tool evidence, and references
to canonical session accounts. Added deterministic synchronization, schema,
tests, CI validation and the ongoing accounting rule. Missing history stays
explicit rather than being reconstructed from token amounts or chronology.

## Collection and corrections

Connected GitHub tools listed 90 PRs and seven issues and returned 307 discussion
comments/review submissions. Full PR fetches for #87/#90 repeatedly failed in
the connector transport; the read-only GitHub CLI fallback supplied their
metadata. Initial issue-detail requests used the wrong repository argument;
the documented repository_full_name argument succeeded. No external comments
or reviewer messages were sent.

Canonical journal attribution uses recorded branch names, explicit PR IDs or
curated narrative evidence. Retained 37 selected journal snapshots from pinned
PR revisions absent on main. They reference upstream account owners without
importing their numeric counters. Seven PR mappings require explicit links
because the original journal records its starting branch or a shared migration.
The workflow documents those links. An initial branch backfill encountered
non-session support JSON; filtering to session records corrected the scan.

The app supplied user-visible messages for 198 exact account-matched turns.
The selected source snapshots retain 1,052 visible messages, including 106
user messages, and metadata for 8,853 exposed operations. Shared PR references
can point to the same turn; these unique-source figures are not sums across PRs.
Fifteen historical threads are unavailable on connected hosts; one accessible
history omits some account turns. Initial oversized pages were recovered using
single-turn requests. Invalid page-size probes were corrected to the app limit.
In total 53 of the 251 distinct account-referenced turns have no retained visible
snapshot. Each PR lists its missing turn keys. These figures describe collection,
not total project usage or a claim of complete historical prompts.

Only explicit user/assistant message items and selected operation/child metadata
are retained. Reasoning, command bodies/results, arbitrary tool arguments,
compaction state and binary uploads are excluded. Conservative path, email,
credential-pattern and external-URL redaction precedes review. Ambient browser
context is removed. Native wrapper calls and operated software are distinct;
installation provenance is unresolved unless supported by recorded evidence.
The source journals were already curated project records, not raw rollouts.

## Implementation and checks

The interaction workflow, schema, standard-library ledger, visible-item allowlist
and regression tests preserve independent PR files and canonical account
ownership. CI requires the current PR record and rejects stale journal/usage
fingerprints. A remote discussion capture is explicitly dated; offline checks
cannot detect later GitHub edits. Capture and source review remain part of each
PR accounting pass.

Eleven new tests, 33 session/recovery tests and ten token-site tests passed.
Session, token, project and interaction validation passed; the existing 234
canonical turns and 740,993,210 observed tokens remain unchanged. The token
preview builds. The paired JSON retains final check results. No geometry
build/runtime activation is needed for this infrastructure change. A sandboxed
process-list inspection was denied; the running backfill was observed through
its existing process session instead.

## Usage

This active parent turn and any separate reviewer turn have no completed,
client-reported exact counters available. Usage is empty, not zero; models and
client version stay unknown. Historical branch/visible snapshots are references
and do not add token observations. The normal later accounting pass must record
closed counters once and synchronize this PR's own interaction file.

## Review and delivery

The initial implementation is prepared for a fixed-revision SoftEng review.
The bounded assignment and findings are appended after its source commit exists.
Publication creates the PR number; its own individual record is then captured
and synchronized in an ordinary follow-up commit. No human approval is inferred.
