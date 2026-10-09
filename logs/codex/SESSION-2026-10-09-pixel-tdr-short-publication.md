# SESSION-2026-10-09-pixel-tdr-short-publication — Publish approved concise pixel chapter

## Scope and evidence

Contemporaneous bounded publication task, parent start
`1b18f2fd728edc2085cf222957e35d53c04d7c9a`, branch
`codex/overleaf-online-sync`. Initial parent changes were the preceding local
short-test tracking, curated note/session pair and PDF output directory; they
were preserved. Clean TDR base was `279d882179e93b56e522fd6b390c965f6ab18e84`.
Primary parent had many unrelated curated log edits/untracked files; those were
not overwritten. Ignored preimages record branch/head, diff hash and status.

Evidence: [publication note](../../docs/publication/pixel-short-publication-20261009.md)
and [source/artifact/check inventory](../../docs/publication/pixel-short-publication-20261009.json).

## Selected conversation

User exact request: “That's great - now push it to overleaf - we like it.”
This explicitly approves publication of the already-reviewed concise pixel
chapter. Assistant fetched the latest source, checked for concurrent edits,
applied the approved chapter verbatim, compiled, normally pushed and verified
publication. The submodule README's general manual-push rule is superseded by
this explicit user instruction. This approval is editorial, not scientific
sign-off or engineering qualification.

## Decisions and outcomes

Overleaf publication revision: `7625cf6054f5761228be6d8d2de24d43f155bd19`.
One normal descendant commit from the authored base changes the approved pixel
chapter, adds its editorial provenance/README note, supplies placeins in the
house style and updates the three wrapper dates. Normal review titles remain.
The five original tables and other chapters/assets/data/generated rows/producers
are unchanged; scientific execution hashes and design lifecycle are preserved.

Pinned local builds are 31 full-report pages and 13 pixel-extract pages. All
pages were rendered and checked; all thirteen pixel renders are pixel-identical
to the approved test. The explicit Overleaf server compile finished with zero
errors and zero warnings. Its one informational underfull-box message concerns
pixel chapter lines 241–243; no clipped or overfull output was observed.
Primary's clean TDR was fast-forwarded safely while unrelated parent work remained.

## Commands and validation

See paired checks. The first file-search path was incorrect and returned an
error; inspection was corrected. Latexmk automatically created its missing
chapter auxiliary directory, then completed successfully; no build failure is
claimed for that internal retry. Local compiler image was the repository-pinned
TeX Live image, linux/amd64, pdfTeX 1.40.29, latexmk 4.88, no network or credentials.
Final logs have no LaTeX warnings, undefined references or overfull boxes.
Only current project source was sent to Overleaf; no client data or credentials
were copied into the repository. Git remote publication was verified exactly.
Online UI evidence is summarized, without private URLs or raw page dumps.
Logger/dashboard, diff checks and final parent publication are recorded below
when complete. These checks assess editorial delivery, not detector acceptance.

## Changes and revision links

Paired JSON inventories current-task changes. Earlier local-test evidence is
retained independently in its canonical session. The TDR revision is a submodule
result and remains separate from parent Git result commits. The existing PR #59
records its pointer and publication evidence; no new PR is needed.

## Token accounting

Exact current-turn counters, model and client version are unavailable. Usage is
empty, meaning unknown, not zero. No active-turn recovery or new schedule was
created. Historical per-turn owners and observations are preserved unchanged;
summary coverage remains partial and excludes current-turn usage.

## Follow-up

Publication is complete. Parent documentation PR review/merge remains with the
human maintainer; no scientific approval or merge is inferred from publication.

## Pre-commit validation

Logger validated 126 records. Summary retains 94 observed historical turns,
57 sessions with usage and 69 without: input 265136032, output 1670036 and total
266806068. This is partial historical coverage, excluding the two recent turns.
Dashboard validated 58 tasks, 31 documents and 19 reviews and built successfully.
A combined whitespace/summary harness read a dependent file before its parallel
producer finished; its read failed and was rerun sequentially. Whitespace checks
had passed. Working/new-file and earlier committed main-relative checks passed.
