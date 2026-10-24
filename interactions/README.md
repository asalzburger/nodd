# PR interactions

Every PR, including infrastructure and closed PRs, has its own
`pr-NNNN.json`. Additional evidence lives under `pr-NNNN/journals/` and
`pr-NNNN/turns/`. There is no shared growing index. Add and update the files for
the affected PR; independent PRs need not edit each other's records.

The initial backfill covers the 90 PRs visible on 2026-10-24, #1 through #97
(issue numbers are not PR numbers). The infrastructure PR introducing this
directory records itself after its number is assigned.

## Reading a record

| Field | Meaning |
| --- | --- |
| `github` | Dated, selected public PR/discussion/review and linked-issue snapshot; login names only, without avatars or email metadata |
| `curated` | Explicit additional session links, agent roles, tool provenance and interactions; preserved by synchronization |
| `derived.parties` | Named GitHub accounts, recorded agents, and explicitly unnamed project users |
| `derived.events` | Actions and reactions typed as comment, issue, prompt, upload, response, review or reaction; source and explicit reply links retained |
| `derived.journals` | Canonical session links, attribution basis and source fingerprints |
| `derived.token_accounts` | References to the sole session owner, exact thread/turn keys and reported models; no copied numeric counters |
| `derived.agents` | Session agents, reported specialist assignments and exposed parent/child thread paths; profile loading is not inferred |
| `derived.tools` | Observed operations grouped by provenance, with their evidence |
| `derived.visible_sources` | Fingerprinted, reviewed user-visible turn snapshots |
| `derived.coverage` | Recovered and unavailable account turns, plus known collection limits |

By the human's policy, GitHub accounts other than `asalzburger` supply human
actions, except identifiable bots. `asalzburger` is recorded as a publishing
account: its messages are responses, without claiming who operated it. Explicit
`@codex` requests from any account are prompt inputs. Review decisions are
reactions. Local inputs keep their exposed speaker identity; an unnamed user
is not silently identified with a GitHub reviewer. A known child thread's input
is attributed to its recorded parent agent.

Public comment replies are linked only by explicit reply metadata or source
links. A local response can link to the visible user input in the same recorded
turn. Other correspondence remains unknown. An upload records its public URL
or the occurrence/type of a local attachment; it does not retain private binary
payloads. Quoted journal text keeps its exact/paraphrase qualifications.

## Tool provenance

| Category | Required evidence |
| --- | --- |
| `native_codex` | Exposed Codex API/operation or integration name; command execution is the wrapper, not the programs it runs |
| `codex_installed` | Recorded installation performed by Codex to support its work, such as the pinned PyMuPDF reader or an isolated plotting environment |
| `instructed_software` | Explicit requested software/runtime and evidence of operation: IdRes, ACTS, Spack-provided DD4hep/ROOT/Geant4, or unrooted and its plotting backend |
| `unresolved` | An operation is recorded but its installer/provider cannot be established; combined historical labels stay here until curated |

Each entry names the operation and its source, version/call count when exposed,
and account. A program's presence or mention is not evidence it operated.
Journal counts and recovered per-turn counts can describe the same operations;
do not add them. Spack availability is not a claim that Codex installed Spack
packages. These records do not require activating or changing any runtime.

## Keep synchronized with PR token accounting

When accounting for a PR, refresh its public inputs and responses, retain newly
available user-visible inputs/outputs and assignment evidence, import verified
closed-turn usage into its canonical session owner, then synchronize and validate:

```sh
# Prefer the connected GitHub tools. ledger.py capture --snapshot accepts their
# selected, sanitized github object with the schema below. CLI fallback:
python3 -B tools/interactions/ledger.py capture --pr 96

# Optional: retain selected branch-only journal evidence from its captured head.
# Fetch that source revision first if it is not already in the local Git store.
python3 -B tools/interactions/ledger.py snapshot-journals --pr 96

# After session_log.py record-usage/import-usage and narrative curation:
python3 -B tools/interactions/ledger.py sync --pr 96
python3 -B tools/interactions/ledger.py validate
python3 -B tools/session_logging/session_log.py validate
python3 -B tools/token_usage/build.py validate
```

Use `sync` without `--pr` when a shared journal affects several existing PR
references. It only writes records whose contents change. It does not contact
GitHub or make a remote snapshot current. `capture` explicitly reads GitHub using
the authenticated `gh` CLI when `--snapshot` is absent; it never posts messages.
Keep the remote capture date visible. Capture and review new public discussion
at each accounting pass; an offline validator cannot detect remote edits.

`tools/interactions/interaction.schema.json` specifies the selected GitHub and
curated input format. `ledger.py` also checks source fingerprints, account/turn
membership, response links and deterministic derived content. CI validates all
records, requires a record for the current PR number, and runs the interaction
tests alongside token validation. Changing a linked journal, usage entry or
retained visible source makes the record stale until synchronized.

For visible messages, explicitly select the journal's recorded thread/turn
through the app's `read_thread`. Feed the selected turn into
`tools/interactions/visible.py:curate_turn` with its exact canonical account ID,
review the result, and save it as
`pr-NNNN/turns/THREAD--TURN.json`. The allowlist retains user/assistant messages,
upload occurrence, operation names/counts and parent/child identities. It drops
reasoning, command text/results, arbitrary tool arguments, context compaction,
images and private state. Conservative redaction is followed by human/agent
review; it is not a guarantee that arbitrary input is safe to publish. Do not
save a raw app response. Unmatched turns must not be assigned by timestamp or
by apparent topic alone.

## Accounting boundaries and historical limits

The corresponding token account remains in `logs/codex/` or `logs/design/`.
A PR can reference several accounts, and one account can be referenced by
several PRs. Those are provenance relationships, not allocations. Do not sum
PR references, split shared turns, duplicate parent/child usage, count active
snapshots, or estimate absent counters. Branch-only journal snapshots link to
immutable upstream owners; their counters are not imported into main.

The initial manual session links cover changes whose journal recorded its
starting branch rather than its eventual PR branch: PR3's planning package,
PR18's accounting/audit package, PR53's shared long-strip study, PR58's beampipe
integration, and PR78–80's staged software migration. Their canonical narratives
describe the publication or staged deliverables. These shared references do not
create additional usage owners.

Full historical conversation coverage cannot be established. The backfill
retains all available account-matched visible turns returned by the connected
app and selected project journals. Some historical threads are unavailable on
connected hosts; unmatched, deleted, other-device and unrecorded inputs remain
unknown. Unavailable turns are listed per PR. Configured model defaults do not
prove execution models. Public discussion is a dated snapshot; deleted edits,
emoji reactions and private upload contents are not reconstructed. Empty
lists mean missing evidence rather than zero activity. No scientific approval
or human sign-off is created by this ledger.
