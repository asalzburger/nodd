# SESSION-2026-09-16-tdr-checkout — Verify local TDR checkout

## Scope and selected conversation

2026-09-16. User (exact quote): “We're good - it's cloned”. Verified the
user-created checkout at docs/tdr, preserving all existing work. This follows the
failed authentication attempt recorded in SESSION-2026-09-16-tdr-clone.

## Findings and outcome

TDR repository is clean on main at
`7783ea3e3235c0fe9da641db3d303a6f211b3073`. Seven tracked files include main.tex,
style/odd-tdr.sty, an introduction chapter stub, README, ignore rules and two PDF
logo assets. The README specifies pdfLaTeX compatibility and a latexmk build.
No nested AGENTS.md was found. No files in the TDR checkout were modified or pushed.

The README describes a submodule in an older odd-2.0 workspace and refers to
assets/literature, docs/spec and PLAN.md. Those references do not establish current
nODD conventions: the actual parent checkout has no tracked gitlink or .gitmodules.
It currently sees docs/tdr as an untracked nested repository. Parent integration
and synchronization policy need a deliberate later decision; no conversion was
performed. Root AGENTS/PROJECT govern nODD evidence and review.

## Validation and changes

Git status, branch, HEAD and tracked-file inventory were checked successfully.
Session validation is recorded in the paired JSON. No LaTeX build, network
verification or detector validation was run. Only this log pair was added; no
commit, design approval or publication occurred. The project-specific remote URL
and credentials are omitted from these records. Exact token usage is unavailable.

## Follow-up

Align template naming/source paths and the chapter plan with nODD when TDR editing
starts. Choose how the main repository pins or retains TDR revisions before
publishing a reproducible release. The checkout itself is ready for local work.
