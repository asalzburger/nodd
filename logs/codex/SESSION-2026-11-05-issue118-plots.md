# SESSION-2026-11-05-issue118-plots — Existing exploratory plots in PR118

## Scope and selected conversation

User, exact request: “Can you integrate the plots into the PR description?”
This authorizes publishing the existing plots. The earlier instruction to
hold the Marlin study remains active. Starting head `1e5fbf71`, working tree clean.

## Changes and evidence

Selected the useful existing electron response and held-out central-muon MIP
figures from the pre-deferral analysis. Excluded the empty muon-only response
figure. Retained compact binwise summaries with edges, units, counts,
normalizations, moments and input/source/config identities. The source summary
identifies `26335fcb381143bc5d29aad0fb405d0d9e22efb9`; no new simulation,
digitization or original-framework comparison was run.

Machine-specific directory prefixes in descriptive metadata are replaced by
portable placeholders; numerical values and original hashes stay unchanged.
The original local binwise-file SHA-256 is retained in publication metadata.
The figure script gained explicit compatibility with the earlier first/second
moment summaries and labels their Gaussian uncertainty approximation; no
higher-moment information was invented. Captions identify the electron-only
sample, held-out calibration split, unresolved forward tails and deferred study.

## Validation and publication

Checked the nine-point electron grid, finite moments, histogram edges/counts
and event denominators. Re-rendered from compact data using Matplotlib only,
then visually checked both PNGs. The PR uses immutable raw Git URLs after the
assets are pushed. Full ROOT samples, caches and run logs stay local/ignored.
Final image hashes/URL availability and journal/ledger/project/site checks
are recorded in the paired JSON.

## Token accounting and follow-up

No exact disjoint per-turn token counters or stable client turn IDs were exposed;
usage stays empty and observed task input/output totals remain unknown.
No private client archives or hidden reasoning were accessed. Keep PR #118 draft
and the Marlin study deferred until appropriate software is installed.
