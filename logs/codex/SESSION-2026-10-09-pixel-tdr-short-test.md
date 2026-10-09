# SESSION-2026-10-09-pixel-tdr-short-test — Local shortened pixel TDR test

## Scope and evidence

Contemporaneous bounded editorial task, starting from clean parent
`1b18f2fd728edc2085cf222957e35d53c04d7c9a`, branch
`codex/overleaf-online-sync`, and clean TDR submodule
`279d882179e93b56e522fd6b390c965f6ab18e84`. No unrelated changes were present
in this worktree at start. The primary checkout was not modified.

Evidence: [local test note](../../docs/publication/pixel-short-test-20261009.md)
and [compiled comparison / file hashes](../../docs/publication/pixel-short-test-20261009.json).

## Selected conversation

User exact request: “Can you produce the shorter TDR version as a test ?”
Earlier user editorial instructions, paraphrased: describe the current baseline,
omit unsuccessful and intermediate design history, and shorten pixel mounting
and cooling prose to suit an accurate full-simulation description. No Overleaf
push was authorized for this test. Assistant produced a separate copied source,
full PDF, pixel-only PDF and editable ZIP, retaining the authored source.

## Decisions and outcomes

The full TDR shrank from 36 to 31 pages; the pixel extract from 17 to 13.
The pixel chapter uses five subsections and eight figure groups. Support,
cooling and service details are compact ledgers. Five original numerical tables
remain byte-identical; other chapters, assets, source data, placement rows,
producer files and scientific execution identities are unchanged. Wrapper
metadata identifies the local test. Float barriers and a reference-page break
keep the figures ahead of the bibliography.

No PR, commit, Overleaf source update or push. Parent HEAD and TDR revision
remain unchanged. Local task tracking does not confer scientific approval.

## Commands and validation

The paired JSON retains actual command outcomes. No host TeX compiler was on
PATH. Initial Docker probes were blocked by sandbox socket access/inactive
daemon. Starting the installed Docker app timed out in the UI but did start
the daemon. The default-platform image pull failed for lack of an ARM64
manifest; explicit linux/amd64 worked. The pinned repository CI compiler image
was used with `--network none --cap-drop ALL`, mounting only the local source
copy. Both original documents and both final test documents compiled with
exit 0, without LaTeX warnings, undefined references or overfull boxes.

An early authoring regex changed citation-key spacing and was corrected before
compilation. An initial export audit rejected whitespace-only differences in
an original table; all five original tables were restored verbatim, both test
documents recompiled, and the final exporter passed. Initial pagination left
figures among bibliography items; float control was corrected and the final
31/13-page PDFs rendered again. An intermediate texcount diagnostic emitted
Perl precedence warnings; its count is not presented as a final measurement.

Poppler rendered every final PDF page. Contact sheets and detailed pages were
visually inspected. Final pixel pages 1–11 match the preceding inspected render
pixel-for-pixel, and final pages 12–13 were individually inspected. Figures,
tables, typography, page numbers and references were checked. Source/archive
integrity, repository logger/dashboard and whitespace checks are recorded in
the paired JSON when complete. These are editorial/build checks, not detector
performance or engineering acceptance.

## Changes and revision links

The paired JSON lists curated notes, local outputs, task tracking and this
session pair. Draft source/build/render files remain under ignored
`build/tdr-short-test-20261009/`. No result commit exists for this local test.
The source ZIP contains the complete editable project and no raw client data.

## Token accounting

No exact counters for this active client turn are exposed; `usage` remains
empty, meaning unknown rather than zero. No recovery or follow-up is scheduled.
Historical observations are neither reassigned nor duplicated. The logger
summary is retained under ignored build output; historical coverage is partial
and excludes this task's current-turn counters.

## Follow-up

Review the two local PDFs and the editable source. Applying this shortening to
Overleaf is a separate action requiring the user's direction. Document/design
lifecycle and scientific approval remain unchanged.

## Editorial closeout — 2026-10-09T11:07:17Z

Logger validated 125 records. Summary retains 94 observed historical turns:
input 265136032, output 1670036 and total 266806068; 57 sessions have usage
and 68 have none. These are partial historical observations, not this turn's
usage or an all-project total. Dashboard validated 57 tasks, 31 documents and
19 review rounds, then built. Final file hashes, source ZIP integrity, PDF page
counts, unchanged HEAD/submodule and whitespace checks passed. Full-PDF open
request was queued in Codex. No publication or new commit occurred.
