# SESSION-2026-10-09-overleaf-online-sync — Online TDR synchronization and pixel shortening proposal

## Scope and evidence

Contemporaneous bounded documentation task. A clean isolated checkout starts at
`896730fd655f2efdfdf8120b27ae750cb3fbd570` on `codex/overleaf-online-sync`.
The primary checkout has unrelated journal/history work; its parent branch,
HEAD and non-TDR diff/status were checked before and after the authorized clean
TDR fast-forward and preserved. No detector configuration was edited.

## Selected conversation

User requested a new documentation PR pulling the latest online Overleaf edits.
User then directed future writing to describe the current baseline, omit
unsuccessful attempts and intermediate steps, and propose shortening the pixel
mounting/cooling discussion for the full-simulation purpose. The user explicitly
withheld an Overleaf push for the proposal.

## Decisions and outcomes

The TDR pin advances from `908e7e539d357738efe223a2d980ab2caa2e5144` to
`279d882179e93b56e522fd6b390c965f6ab18e84`. Only the three authored subsystem
chapters changed in that online revision. Figures, generated tables, input
snapshots, producers and previous provenance manifests are unchanged.
The primary clean TDR main was also fast-forwarded to the authored revision.

Persistent TDR writing guidance is linked from AGENTS.md. The pixel proposal
provides a five-subsection structure, eight principal figure groups, compact
parameter ledgers and replacement support/cooling, routing and material prose.
It remains an editorial proposal in nODD. No TDR source edit or Overleaf push,
scientific change or design approval was performed.

## Commands and validation

Git fetches, isolated worktree creation and TDR initialization succeeded.
`verify.py` in the ignored build directory verified the exact head, clean
submodule, fast-forward relationship, unchanged nonchapter tree, 35 bundled
snapshot/producer/artifact hashes, TeX input/graphic existence and thirteen
current pixel figure environments. The ignored source-checks JSON retains this
result; curated chapter hashes are in the publication inventory.

Overleaf main.tex recompiled with pdfLaTeX/TeX Live 2026. The UI showed Errors 0
and Warnings 0; raw compiler output reported 36 pages / 2,781,840 bytes. This is an
observed source compile, without a retained PDF or all-page visual QA claim.
Local pdflatex/latexmk were unavailable; Overleaf provided the compile check.
The first logger validation and summary rejected the new activity entries because
they omitted required schema fields. The entries were corrected to the repository
schema. Additional logger, dashboard, Git and hosted results are recorded in paired JSON.

## Changes and revision links

Changed files are enumerated in paired JSON. Earlier publication and native
execution identities are preserved. The actual parent pin is independent of
those scientific execution hashes. Future proposed figure combinations are
not presented as already rendered artifacts.

## Token accounting

Exact counters for this active client turn are not exposed; usage remains empty,
meaning unknown. No partial recovery, estimates or duplicated historical counts
were imported. Logger summary reports only previously observed disjoint usage;
older project coverage remains partial.

## Follow-up

Review and merge the documentation sync PR. Review the pixel editing proposal
before applying it and publishing an agreed revision to Overleaf.
