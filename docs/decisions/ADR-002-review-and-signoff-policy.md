# ADR-002 — Review and sign-off policy

- Status: DRAFT
- Created: 2026-09-15
- Human owner: TBD
- Issue: TBD
- Supersedes / superseded by: None
- Human approval evidence: Pending

## Context and evidence

[AGENTS.md](../../AGENTS.md) already requires human sign-off, exact design traceability, and separation of design approval from production implementation unless a human maintainer explicitly permits an exception. [PROJECT.md](../../PROJECT.md) defines review roles and the design lifecycle. This proposal fills in review assignments and enforcement; it cannot weaken those rules.

## Options

| Option | Benefits | Costs and risks |
| --- | --- | --- |
| Assign reviews separately for each proposal | Adapts expertise to scope | Can leave approval requirements unclear until late |
| Maintain a reviewer map with scope-specific requirements | Makes required expertise and routing visible | Requires maintenance and handling unavailable reviewers |

## Proposed decision

**NODD DESIGN CHOICE — pending human approval:** maintain a human reviewer map by subsystem and cross-cutting expertise. Before review, identify technical, domain-expert, approval, and validation responsibilities for each substantial proposal.

Propose technical review and relevant domain-expert review before design sign-off, followed by validation review before acceptance. The minimum number of distinct people, author/reviewer independence requirements, and permissible role combinations remain open for human decision.

Use GitHub issue/PR links for discussion and approval evidence. Sign-off must name the reviewed full commit SHA, human reviewer and expertise, date, outcome, conditions, reservations, and superseding decisions. Use the [sign-off template](../signoff/TEMPLATE.md). A merge or AI-generated approval text is insufficient.

## Enforcement and verification

After policy approval, configure `CODEOWNERS` and repository branch rules for governed paths. Verify that configured rules enforce the agreed review policy. These controls have not been configured by this document.

Changes after review must remain traceable; humans must assess whether amendments require renewed review. Never move approval to a new revision automatically.

## Open questions and human review

- Who is the maintainer and who can authorize implementation and acceptance?
- Which experts cover sensors, electronics, mechanics, thermal systems, services, simulation, and reconstruction?
- How many distinct reviewers are required, and may authors hold approval roles?
- How are conditional approvals resolved and recorded before implementation?
- Which repository protections are available, and who configures them?

Reviewer assignments, reviewed revision, review date, outcome, and approval evidence: **pending**.
