# SESSION-2026-09-17-dashboard-pages — Pages deployment chore PR

## Scope and evidence

Contemporaneous curated infrastructure task, starting at
595a394 on chore/dashboard-pages with a clean working tree. Exact starting SHA
and initial state are in the paired JSON. Existing unpublished dashboard commits
are included in the requested chore PR; no separate open dashboard PR existed.
Exact token counts and client identifiers are unavailable.

## Selected conversation

User (exact quote): “ok, make a chore-pr to deploy this as a github page - and make
a rule to always update it. chore-pr's are excluded from the progress tracking”.
Assistant outcome: prepared Pages workflow, mandatory maintenance rule and update
CI checks; excluded infrastructure chores from progress while retaining history.

## Decisions and outcomes

Workflow builds/tests every PR; main pushes and manual main runs package the
allowlisted site and deploy through github-pages. PRs never deploy. Build permissions
are read-only; Pages/OIDC permissions are confined to deployment. Main workflows
are serialized and every successful main push rebuilds the site, including chores.

AGENTS.md now requires same-PR tracking/review updates for non-chore project work.
CI checks actual changed paths and the chore title convention. Chores are excluded
from progress tasks/PR/review records and cannot mask scientific changes. Removed
the prior dashboard infrastructure task from progress; its historical records remain.
Added PR template, regression tests and maintenance/recovery documentation.

Reviewed official GitHub Pages/action/API documentation (2026-09-17). Initial
sandbox API reads failed; escalated reads confirmed no Pages site/environment.
Configured Pages with build_type workflow and a custom main-only environment
branch policy. This prepares publication after merge; no branch or site was deployed.
No detector parameter, formal approval state or scientific-source provenance changed.

## Commands and validation

25 dashboard/update-policy tests, 15 logging/documentation tests and 14 JavaScript
assertions passed. Workflow YAML/deployment conditions checked. Site build validated
10 project tasks, 7 documents and 3 reviews; 160 local links across 22 output pages
checked. 28 session records validated; whitespace check passed. Actual commands and
API outcomes appear in the paired JSON. Hosted PR CI is checked after PR creation;
real browser/mobile and first deployment remain unverified until performed.

## Changes and revision links

See paired inventory for workflow/template, maintenance instructions, schemas,
tracking corrections, validators/tests/guides and this session pair. The new
chore PR itself is intentionally not entered into project progress tracking.

## Follow-up

Open the requested chore PR and verify hosted CI. Human merge triggers the first
main-branch publication at https://asalzburger.github.io/nodd/. Production geometry
and existing design lifecycle remain governed by normal human sign-off rules.
