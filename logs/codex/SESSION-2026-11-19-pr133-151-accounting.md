# PR133–PR151 interaction, token and simulation accounting

## Selected user request

User, exact: “Can you give me a token and interaction, work accounting of PR133 through PR151” covering user-agent interactions, tokens, simulation counts and available durations.

## Outcome

See [the complete report](../usage/AUDIT-2026-11-19-pr133-151.md) and [compact machine-readable evidence](../usage/AUDIT-2026-11-19-pr133-151.json). Available histories contain 56 user chat messages/51 user-initiated turns, plus three public request inputs. The deduplicated observed subtotal is 1,067,294,375 tokens/168 turns, including four newly closed observations. Retained evidence identifies at least 67 transport attempts, 63 successful/4 failed, 201,805 successful event executions, plus nine initialization probes. Fifty-nine timed transport attempts sum to 5.372 process-wall hours and 43.827 CPU-hours. Missing counters/durations stay unknown. No simulations were launched for this audit.

## Commands and evidence

- Read applicable AGENTS.md, PROJECT.md, logging and interaction workflows; preserved existing work by creating the dedicated codex/pr133-151-accounting worktree at78bef505c4e623739da204ce92e3aa7bc6f931c5.
- Connected GitHub fetch_pr for133–151 verified current title, branch/head, merged status and discussion; selected public metadata refreshed in each PR ledger.
- Connected read_thread paginated both main chats, selecting only user-visible user/assistant messages. Counted stable message and turn IDs, including steering and interrupted requests; excluded duplicate journal/curated rows and agent-to-agent messages.
- Used immutable Git sources3ebafd340b0e084c5e42e57123de115e3f489244,78bef505c4e623739da204ce92e3aa7bc6f931c5 and0babd0cfcf6f6094e09583abce3a88bfd5f99e8d for the distinct PR stacks. Deduplicated164 canonical observations by exact thread/turn.
- recover_usage.py --codex-home /Users/salzburg/.codex --thread-id <selected known thread> --output <new temporary inventory>: successful direct recovery of13 contributing threads; the older ECAL primary fails inherited-prefix reconciliation. Diagnostic suffix recovery also failed ownership comparison and was discarded. No weakened validator or unverified counters were used.
- Recovered four disjoint, closed primary observations from the LAr chat, matched to their connected user-visible request and exact turn IDs. Imported PR140 and PR146 preparation turns into their original paired session owners after dry-run. This new bounded accounting owner holds only the two previously unowned LAr feasibility questions,2,677,057 tokens; its PR138 association reflects that historical task. Current audit consumption remains unknown.
- Inventoried local transport receipt.json and placement timing.json records plus source-pinned committed reports, distinguishing transport launches from initialization-only probes. Deduplicated analysis copies and re-used samples. Excluded native geometric/ray checks, readback, fits, bootstrap and plotting from simulation counts.
- session_log.py import-usage dry-run/import for the three owners; ledger.py snapshot-journals for135–137/148–151, followed by per-PR synchronization and validation.

## Scope and limitations

Infrastructure accounting only; no design/ADR/geometry/physics changes, engineering approval or science tracking entry. PR152 and later work excluded. Branch-only accounts remain immutable references, not copied project usage owners. The current audit is excluded from the historical range totals. Raw client archives, hidden reasoning, full simulation files and bulky logs are not retained in Git. Canonical source revision/counter links and selected visible user inputs are in the compact audit.

## Checks and draft delivery

Final validation and draft PR URL are recorded below when observed.

Validation passed:305 session records;111tasks/54documents/24review rounds;130PR ledgers;593disjoint canonical project turns/3,379,733,598observed project tokens; token preview build under`_site/pr133-151-token-preview`; independent range arithmetic and136existing observations reverified; whitespace checks. The old dashboard build path is absent and was replaced by the repository's current project_records validator. An initial token preview path under build/ was rejected; the required _site/ path succeeded. No detector/runtime tests or simulations were necessary for this accounting-only change.

Draft delivery: [PR153](https://github.com/asalzburger/nodd/pull/153), `codex/pr133-151-accounting` → `main`. Initial commitc939ec3e retains the completed report. The connector denied PR creation with403, so the authenticated GitHub CLI fallback created the verified draft. No ready-for-review or merge action was taken. The draft's own interaction record is added in the closeout commit.
