# Selected trimmed pixel baseline in DD4hep and TDR

## Requests and scope

On2026-10-06 the user requested two separate follow-up PRs: update DD4hep for
the new trimmed endcap with single/quad modules, then update the TDR. The user
selected self-contained TDR sources in nodd rather than an Overleaf push.
Original pT>=1GeV/eta/luminous-region assumptions remain those of DES018.
This is a new bounded task, canonical token owner once for both PRs.

## Starting state and actions

Started client turn01a11051-efc0-75e1-8080-8c9c88d42e24 at2026-10-06T08:26:07Z,
thread01a10c6a-664d-72b1-afad-926c2c57312b. PR43 merged at08:23:13Z into prototype
parent codex/issue38-disc-overlap at7057861fa3c8c137833ecedddcae0856ebd91e4c.
Created separate codex/pixel-baseline-dd4hep checkout from that merge. Original
main and preexisting untracked primary logs preserved. Initialized clean TDR
submodule at7783ea3e3235c0fe9da641db3d303a6f211b3073 for template inspection.

Read root AGENTS, PROJECT, logging and relevant DES/ADR/publication contracts,
TDR README and ACTS sister instructions. Created DES019 before implementation.
New default config preserves frozen legacy pins. Implemented source adapter,
radial/tangential proper frames and reversible source-ID mapping, chip pickups,
retained cooling rows, disjoint effective support and heterogeneous transport.

## Actual checks and corrections

ACTS Spack preflight failed changed setup/lock fingerprints; user warned before
runtime work. Actual imports verified DD4hep1.38/ROOT6.40.04/Geant411.4.2. Missing
local TeX commands caused the availability shell exit1 after successful runtime
imports; no shared dependencies installed/changed. Existing sister edits preserved.
Usage-recovery first failed because the output parent was absent, then succeeded
into ignored build/issue38; current turn remains active, so no partial usage import.
Some exploratory reads used wrong filenames/globs or inspected integer `stems`
as a list; corrected from actual directory/files/schema. No scientific changes
followed these read errors.

Pure export and9 focused tests passed. First native workflow passed6/6 CTest and
Geant4 initialization. After source parameter centralization, final workflow
passed6/6 CTest, portable nodehammer/display audits and Geant4 initialization,
zero events, seed42, FTFP_BERT. It contained8 exporter tests; the added ninth
Ti/CO2 conservation check passed separately. Retained DES019 artifacts record
actual dirty producer/input/plugin hashes at starting merge7057861; never replace
those hashes by an enclosing commit. No legacy evidence regenerated.

## Limitations and accounting

DES019 remains DRAFT/PROTOTYPE despite human preliminary-baseline selection.
Coverage holes, warm-thermal/guard failure, service packing failures and
manufacturing interfaces remain open. Current turn final resource counters are
unknown until closure; recover only this exact turn once into this record.
Execution model/client version unknown; older project coverage partial. No
all-project or self-inclusive current total claim. TDR work and publication
closeout will be appended here; no duplicate token owner.

## Initial PR publication and TDR preparation

Model deliverable9a4632d8262fb7667be80c168635d4c9eac8317e normally pushed and
PR44 created/attached. Hosted run37440107590/job112191489402 succeeded on that
head at2026-10-06T09:07:48Z; deployment skipped. TDR branch starts at that model
commit. Self-contained sources/figures/evidence committed6d709ead4e1a9d8fc82ec807bd93a758d82503c0,
normally pushed; PR45 created/attached stacked on PR44. No Overleaf mutation.

TDR generator first failed because Matplotlib was absent from bundled Python
and unactivated ACTS Python. No installation performed; activated existing Spack
plotting runtime succeeded. Premature --check failed absent evidence manifest;
then generated/check passed. A malformed apply_patch hunk was rejected without
mutation and corrected. Dashboard rejected invented PubDoc task role; reused
registered Publication/documentation office. Build rejected .tex deliverables
under its curated-text export rule; tracking points to manuscript/tool READMEs
without weakening the builder. Corrected validate/build passed45 tasks.
Generated figure labels enlarged for publication scale; figures visually checked.
PDF skill marker ran once. Actual compilation and page inspection pending CI.

TDR initial pdfLaTeX run37441168602/job112194993933 failed at the booktabs
bottom rule with `Misplaced noalign`: the input macro was inside the alignment.
Corrected generator to include the complete tabular block, with manuscript input
outside alignment. Added a source-derived unchanged barrel table and clarified
that endcap active axes differ from barrel axes. Preserved the failed attempt.
Repair commit89b4ce289c2f700e91315a529c600a36317f84fc normally pushed.
Pinned the exact TeXLive2026 container digest observed in that run; no font or
engine substitutions, shell escape, scientific rerun or gate weakening.

The repaired PDF run37441899296/job112197406343 succeeded on89b4ce2 at
2026-10-06T09:19:18Z. Downloaded its PDF/log, rendered all11 A4 pages with
Poppler and inspected each page. No clipping or unresolved references. A long
module paragraph was interrupted by deferred figures; added a float boundary
before the module section and reran compilation for clearer reading order.
Clarified contract text in63e030f2b517bdbe526a1860c0f32a3012a712b4: core insert
is4.50mm plus0.15mm skin window (4.65mm combined), as already implemented and
validated. No material/geometry input changed; quad ASIC opposite peripheries
spelled out. TDR references that immutable correction and hashes its source.
Ordinary parent merge preserved both branches; final text refinement published
dda70e5709e1668dfe98e555dddda8efbccd13a8. Removed duplicate push-triggered PDF
builds, preserving PR and manual compilation; validation gates unchanged.
Sandbox plotting emitted denied CPU sysctl probes but completed successfully;
all generated asset hashes/checks passed. Final page-flow build is pending.

A second authorized metadata-only recovery confirmed exact current turn
01a11051-efc0-75e1-8080-8c9c88d42e24 remains active, start ordinal4235 and no
end ordinal. Partial counters were not imported or represented as final.

## Final manuscript review and merged model PR

Final pdfLaTeX run37443298638/job112201993926 succeeded on
`dda70e5709e1668dfe98e555dddda8efbccd13a8` at2026-10-06T09:31:05Z.
Downloaded final11-page A4PDF and public compiler log, rendered all pages at105dpi
with Poppler and inspected every page. Tables/figures/citations/page numbering
are legible, with correct paragraph flow and no clipping or missing glyphs.
Compile gate reports no overfull boxes or undefined citations/references.
Retained `docs/validation/DES-019-tdr/` includes PDF/log and exact source/artifact
hashes, distinct from subsequent metadata commits. PDF SHA256 is
`d20dead332949176b166e1c0b43a0f1d94050831efdf2f1eb04823fd4fdadfa2`.
Hosted dashboard/regressions run37443298649/job112201993859 passed on the same
head at2026-10-06T09:35:39Z; deployment skipped.

PR44 was discovered merged during this task: actual head9a4632d, merged
2026-10-06T09:11:30Z as38255171eaa3e211da3bc1eebfcaead3b749807a into
codex/issue38-disc-overlap. Codex did not merge it. No further push to PR44.
The later63e030f contract wording correction (executed material unchanged)
is retained in PR45. Normally merged the receiving parent into the TDR branch
and retargeted PR45 there. Final TDR evidence/tracking/shared log publish in
PR45; logger owner stays the same shared record, never split between PRs.
Model checkout retains curated uncommitted copies of its pair and PR44 snapshot.

Native execution hashes, earlier controls/evidence, service radii and engineering
failures remain unchanged. No Overleaf push, production integration or sign-off.
Active turn counters and actual client end time remain unknown; one bounded
after-close recovery will import only the exact shared implementation turn.

Final source/figure/table hash check passed. Logger validates103 task records;
summary records older partial coverage and excludes this active turn.
Dashboard validates45tasks/25documents/19review rounds and builds under
_site/pixel-tdr-closeout. Working-tree, full parent and origin/main relative
diff checks pass. Safely synchronized only the shared pair into primary after
verifying the saved absent preimages. Primary validates109 records, stays on
original main7b559d0 with scientific files unchanged. Model local pair also
validates103records. Remaining client-end timestamp/token measurements will be
filled by a single bounded after-close metadata-only recovery, without changing
scientific inputs, execution hashes or assigning the turn to another record.

The first staged closeout diff check exposed native whitespace in the public
TeX compiler log; a following stat masked the shell exit and metadata commit
14258a2 still executed. Preserved this failure and corrected in ordinary history:
the compiler log is now stored as byte-preserving gzip with independent raw and
compressed hashes. No PDF/manuscript/native evidence changed. Future checks
run with explicit failure propagation.
