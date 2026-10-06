# SESSION-2026-10-06-overleaf-pixel-baseline — Existing Overleaf pixel baseline update

## Scope and evidence

Contemporaneous bounded editorial/publication task from parent main
`e50ae6def313cae3d9be62ff1e299569965c1b35`. Six unrelated untracked historical
session files were present and preserved. The initialized TDR gitlink pointed at
`7783ea3e3235c0fe9da641db3d303a6f211b3073`; the latest existing report main was
`045445eb833cc0ce5a481c30c4220e1bf7af3e96`, containing the detailed barrel and older
quad endcap. Work used that latest report revision.

## Selected conversation

User request, paraphrased: update the initialized Overleaf TDR text and drawings
to the new pixel baseline, preserve its close-to-final barrel description, and
push the changes to Overleaf. The user subsequently stated: “Codex browser is
signed in.” These instructions authorize the existing report update and ordinary
remote push. They override the inherited report README's generic “Do not push”
rule for this bounded task; they do not establish formal design sign-off.

## Decisions and outcomes

Updated the pixel chapter to the current main working baseline: four single rings
plus two quad rings before the station-dependent inner-single-ring removals. The
report now retains the current integer disc datums, survivor polar axes/IDs,
module/chip/circuit counts, support geometry, pickup/stem arrangements, fixed
service boundaries, transport inventory and current mass totals. The removal
assumptions and coverage/guard/warm-thermal/fixed-service-packing failures remain
explicit, with preliminary support/cooling/mounting qualification limits.

Preserved the detailed barrel layout and barrel electrical/cooling text blocks
byte for byte, together with the barrel snapshot, figure assets, editorial routes,
bibliography, style and report entrypoints. Introduced a separate current-endcap
snapshot and provenance file instead of overwriting the frozen historical barrel
snapshot. A deterministic endcap-only generator updates the overview, disc plans,
disc section, cooling/service routing and external service-interface PDFs, plus
the endcap tables. The first and last disc plans expose the aperture change at
the same transverse scale. Generated data retain actual source/input/native
identities; the enclosing publication commit is not an execution identity.

Committed and normally pushed the report to its existing remote main at
`72bb502dfe09a1a1209acbf7b5c048094b652e1e`. Remote main was verified equal. The
parent pointer/publication record was committed at
`14c3816ed7b531dd877f1b37cbabc47bcfee0cc8` on `codex/overleaf-pixel-baseline`
and normally pushed. [PR48](https://github.com/asalzburger/nodd/pull/48) is OPEN
against main and attached to this task. Initial sandboxed PR creation could not
connect to the GitHub API; authorized network escalation succeeded.
[The publication inventory](../../docs/publication/pixel-baseline-overleaf.json)
contains the exact source/artifact hashes and engineering boundaries, without
private project URLs, authentication data or raw conversations.

## Commands and validation

- Pure deterministic combined exporter: 5362 modules,11806 active chips and
  100334 entities; current material and transport totals reconciled. This was
  not a new DD4hep/Geant4/ACTS execution.
- `scripts/pixel_baseline_snapshot.py --source-root ../.. --expected
  ../../build/issue38/overleaf-baseline/export/expected.json`, followed by the
  task-venv `scripts/pixel_figures.py --endcap-only`: passed. All19 retained
  artifact hashes and listed parent source hashes verified.
- Initial runtime/system matplotlib imports failed with ModuleNotFoundError;
  resolved with matplotlib3.11.2 in an ignored task-only venv. No shared dependency
  installation. No local TeX engine was available; compilation used Overleaf.
- TDR `git diff --check`: passed before commit; ordinary push and remote-head
  verification passed. Detailed barrel and unchanged asset checks passed.
- Actual signed-in Overleaf pdfLaTeX build and explicit final Recompile passed:
  23 A4 pages, UI zero errors and zero warnings. Raw log retains two inherited
  PDF-version inclusion warnings for unchanged odd-mark.pdf and
  pixel-module-edge.pdf. No LaTeX warnings, undefined references or box overflow
  warnings were found. Actual engine is pdfTeX1.40.29/TeX Live2026.
- Compiler-reported output is837891bytes; downloaded optimized PDF is843096bytes.
  These are separately hashed artifacts, not claimed byte-identical. Final log
  starts2026-10-06T13:03Z at minute precision; downloaded PDF metadata is
  2026-10-06T13:03:46Z. Exact compile-completion time is not exposed.
- Rendered and visually inspected all five revised figure PDFs and all23 report
  pages. Tables/captions/layouts fit. Fresh final PDF text matches all23 pages
  of the earlier rendered/inspected PDF. Saved actual Overleaf proof screenshot
  and final PDF/log under ignored `build/issue38/overleaf-baseline/`.

Initial parent logger validation rejected a browser PASS observation with a null
process exit code. Replaced that entry with a successfully executed Python
assertion over the retained compiler log and PDF; no fabricated service exit
code. Dashboard validate/build passed45tasks/25documents/19reviews, and working
plus full start-relative whitespace checks passed. Corrected logger validation and summary passed115 records; this task has no
observed token counters. Hosted parent checks are recorded only when observed. No design lifecycle, scientific inputs, older evidence or
native execution hashes changed.

## Changes and revision links

The paired JSON inventories the parent gitlink, focused publication record,
tracking update, current session pair and16 changed report files. Report result
commit is72bb502; parent result commits are recorded only after they exist. Git
history identifies the enclosing record revision without a future self-hash.

## Token accounting

Exact current-turn counters and client version/execution-model identity are not
exposed while this implementation turn is active. `usage` remains empty: unknown,
not zero. No estimates or cumulative client counters were imported and no older
observations were duplicated. This task's logging does not establish a complete
project total; older record coverage remains partial. Start/end client timestamps
are null because they were not observed. Closed status denotes bounded delivery,
not scientific acceptance or an observed client-turn closure.

## Follow-up

Human editorial review and parent-pointer integration remain separate from the
successful requested Overleaf push. Engineering qualification, physical detailed
routing and the retained adverse screens remain open under DES016–019, all DRAFT.
No whole-report release or detector acceptance is inferred from the PDF build.
