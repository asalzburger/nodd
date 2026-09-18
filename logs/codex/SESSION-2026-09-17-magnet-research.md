# Magnetic configuration research — first increment

- Date: 2026-09-17; branch: `research/magnetic-configurations`.
- Governing IDs: DES-004, DES-003, ADR-006; isolated PROTOTYPE research.
- Exact token counts and client thread/version were not exposed; usage remains unknown.

## Selected user requests

- “Ok, I like the plan, go loose”: execute the discussed magnetic research plan.
- “Can you do `pip install pyacts` instead?”: use the official tracking package.

## Starting state and synchronization

Local main was behind the merged envelope and dashboard work. Preserved the four
planning files in commit `8e569d4`, then merged origin/main (`60ef366`) into the
new research branch as `7850263`. The sole conflict was the source catalogue:
retained the complete newer catalogue plus the two planning source records.
No unrelated work or TDR submodule state was changed. Initial Git writes required
sandbox escalation; ordinary merge preserved history.

## Work and team contributions

- Coordinator/Publication: integration, canonical proposal, logging, tracking,
  independent Biot–Savart tool, plots and validation report.
- System Architect: six candidate cards and explicit outer-coil envelope amendments.
- Calorimeter, muon and tracker agents: separate sourced consequences and questions.
- Physics: common diagnostic contract and independent 384×512 quadrature review.
- Software: verified official `pyacts`, isolated installation and ACTS checks.

The initial plan correctly distinguished public PyPI `acts` from tracking ACTS,
but missed the official `pyacts` distribution. The user's correction was verified
against the official ACTS repository README, applied to the protocol and source
catalogue, and used for installation. `pyacts==47.7.0` installed successfully in
ignored `reference/cache/acts-venv`; root independently imported `acts` and checked
the required field/stepper/propagator names. Detailed checks are in the setup report.

## Numerical evidence and corrections

MAG-01 and MAG-03 are explicitly vacuum controls: thin current sheets, 3 T central
normalization, no iron/material. Six field unit tests passed, with axis, parity,
reversal, Maxwell identities, convergence and asymptotic checks. The independent
physics review reevaluated all twelve benchmark positions at finer quadrature.
It identified a weaker unit-test tolerance and invisible colour clipping; root
aligned the test with the comparison contract and added colour-bar extensions.
The benchmark and atlas were regenerated. Masked atlas cells remain unresolved,
and the displays are not interpolated transport maps.

The outer-coil space proposal conflicts with a common muon diagnostic surface.
All relevant documents flag this; a point inside the proposed coil cannot count
as an instrumented measurement in a physical candidate comparison.

## Validation and remaining scope

Commands and final results are recorded in the paired JSON. Initial link tests
failed on two references to the not-yet-written ACTS report during concurrent work;
retain that history and rerun after integration. A dashboard validation initially
rejected a combined role label; corrected it to the register's System Architect
role while preserving team responsibility in the scope. No test was weakened.

No production geometry, material, reconstruction configuration, design sign-off,
physical field ranking, momentum resolution or shower-containment result is
claimed. Nonlinear steel/yokes, discrete toroids, validated transport maps,
material/measurement comparisons and candidate selection remain subsequent work
behind the protocol's review gates. All candidate parameters remain unsigned.

## Delivery

Committed the first increment as `bac4d4ee7cedece2b64f2d679dfebbe3197f05f1` and opened [draft PR #6](https://github.com/asalzburger/nodd/pull/6).
The dashboard records a pending technical review at that exact design revision.
Seven ACTS propagation fixtures and five axis comparisons passed the final root
run; all 15 documentation/logging tests passed after integration. The bounded
first-increment session is closed; the wider magnetic research remains active.
