# SESSION-2026-11-14-lar-gap10k — conditional gap response

## Selected requests and scope

> Can you run the standard 19k electron sample and see if the barrel-Endcap gap improves ?

Correction:

> 10k sample this is

The interrupted 19k turn ran no tools. This bounded task uses10,000 standard
matched primaries. Previous PR143 is standalone at unchanged calorimeter
positions; it has no gap reduction to measure. Coordinator stated the conditional
800→400mm warm-gap test before new showers: translate whole signed endcaps,
keep internal material/readout/local services and fixed barrel, no unresolved
pipe overlay or wall cuts. This is response sensitivity, with physical interface
prerequisites still open. Governing prospective protocol is
`docs/validation/lar-gap10k/protocol.md`; user request authorizes the isolated
experiment, not production adoption or engineering sign-off.

Repository/nodd-coordinate/design-evidence/review-validation and acts-spack
instructions read. Preflight on acts-mac-studio-01.cern.ch exited2 with changed
setup_script/spack_lock fingerprints; user warned before dependencies. Fresh
software/env/run.sh imports verified ROOT6.40.04 and DD4hep/DDG4. Sandbox sysctl/ps
warnings did not prevent this. No shared dependency install/staging/update.
New task worktree/branch codex/lar-gap-10k-response starts at
8dfa8573f4a3e278db4a882d99a25a0df8109dc5 (draftPR143).

Initial discovery mistakenly searched all sibling worktrees and produced bulky
filename output; subsequent searches are bounded to the selected checkout.
No files were changed by that search. Existing full10k LAr and SiW primary
artifacts are present;253GiB free at inspection. Destination was reverified as
the same public asalzburger/nodd repository1361703051 with push permission.
