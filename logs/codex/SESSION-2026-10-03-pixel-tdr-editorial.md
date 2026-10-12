# SESSION-2026-10-03-pixel-tdr-editorial

## Request and outcome

User requested a larger text block with less margin; internal nODD decisions
must be explained in the TDR rather than cited; barrel services in Figure 2.1;
use the compact-module SVG from unmerged PR #8 to inform Figure 2.3; cables and
color legend in Figure 2.5; color legend in Figure 2.8.

Text width increased from 124 to 150 mm; side margins 43→30 mm, top 32→25 mm,
bottom 41→28 mm. Body fonts/leading remain readable and unchanged. PubDoc rewrote
the two chapter files to incorporate physical rationale and leave seven public
bibliography entries. Internal decisions, generated inventories and PR revisions
are preserved in source provenance, without publication citations. The rationale
covers module interfaces, guards, populations, support and spreader widths, tube
loads, ring restraint, alternating disc faces/heights, pickups, carrier and cables.
The already-catalogued NIST density table was added to the report's source subset;
the public catalogue and detector design parameters remain unchanged.

Figure 2.1 adds positive-side cable envelopes for all four barrel layers, schematic
cooling paths and extraction detail. Figure 2.5 projects all 82 exact terminal cable
sectors and has a color legend; Figure 2.8 gains a color legend. Figure 2.3 keeps its
quantitative stack and adds the PR #8 common accessible-edge panel showing pads,
wire access, discrete illustrative bumps and coverlay construction. The optional
two-chip/alternative panels are omitted. The adapted SVG and its pinned original
hash are retained. No manufactured bump/loop dimensions are inferred.

## Revision and verification

Starting parent: 1bfe400fc2df895bb503857f50a4c1f96a3c3b78.
Starting TDR: 952483261d24c3a856ab8f9f33e26a039fa1ec9a.
PR #8 source: 214747a3c83c140caa6c4ae9c3fb6486ac5cb825.
Work stayed in the isolated documentation checkout; unrelated user files were
preserved. Existing human authorization covers ordinary Overleaf synchronization.
No geometry, acceptance, human approval or sign-off state changed.

Checks actually run: both latexmk wrappers; whole-report raster review and targeted
figure review; citation key/bibliography consistency; no internal citations;
82 terminal / 80 longitudinal record verification and sector-area arithmetic;
editorial SHA256s;19 generated artifact hashes and repeat rendering; independent
packaged-source builds; staged whitespace; dashboard validate/build. Initial
widened build had one 9.55 pt overfull ring-position line; equivalent symmetric
notation fixes it. Final PDFs are 22 pages for the full report and 18 for the extract,
with 13 numbered figures and two panels in Figure 2.3. No detector runtime is needed.

Exact client-reported per-turn tokens are unavailable for parent and PubDoc;
usage remains empty and no estimates are recorded. Historical usage summary and
final publication revision are recorded below after verification.

Overleaf ordinary push and independent remote read verified final TDR revision
`78abe8b23271b1e85f36065ba2bf8ad5ab40bdee`. The final colophon wording now also states
that design choices are explained in the text and public literature is cited.

Final package verification passed for 42 artifact hashes and both independent
build logs. Logging validation passed for 78 records. Summary observed historical
input/output is 134,594,309 / 674,111 across 79 turns in 42/78 sessions.
Thirty-six sessions lack usage measurements, including this task; these historical
totals are not current-task usage.

## Token-accounting correction — 2026-10-12

This historical session pair was restored from local branch revision
`7ec9d05dc5ee9aefdf6c0da30549615ebc06a0b0`. The original narrative and checks
remain historical evidence; its publication artifacts are not restored by this audit.

Imported 2 verified closed turns: **7,001,830 input** and
**24,665 output** tokens. The [device audit inventory](../usage/USAGE-2026-10-12-device-audit.json)
retains exact boundaries, request counts, event hashes and task attribution.
Parent and PubDoc observations reconcile independently from zero; the recorded
parent edge and child-turn completion activity establish the assignment.
Earlier missing-counter statements describe the original capture. Cached input
and reasoning output are subsets; execution model/client version and total project
coverage remain unknown. No design approval or scientific validation changes.
