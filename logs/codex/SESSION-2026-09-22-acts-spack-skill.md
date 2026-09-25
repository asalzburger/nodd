# SESSION-2026-09-22-acts-spack-skill — Node-aware ACTS Spack workflow

## Scope and selected request

User asked to learn the node-specific workflow exposed by sourcing
`/Users/salzburg/cernbox/configs/acts/acts_setup.sh`, focusing on `setup_spack`
and preinstalled DD4hep/Geant4 libraries and sources. They explicitly asked to
record supported nodes and warn when requests rely on an unavailable workflow.

Starting Git revision/branch and the preserved unrelated tracker bytecode are
recorded in the paired JSON. Exact tokens/client details are unavailable. The
skill-creator instructions were applied; the validated skill was installed in
the personal Codex skills directory with filesystem approval. Repository files
remain the canonical, portable skill source and node registry.

## Findings

Only acts-mac-studio-01.cern.ch was inspected. The helper activates the existing
ci-dependencies Spack environment. DD4hep 1.37 with DDG4 and Geant4 11.4.1 are
installed, including headers and CMake packages. Python is 3.14.5. Spack revision
and package hashes, setup/lockfile fingerprints and verification date are in
skills/acts-spack/references/nodes.json and workflow.md.

setup_spack alone is insufficient for DD4hep Python imports: DD4HEP_LIBRARY_PATH
is absent. Sourcing thisdd4hep.sh and geant4.sh permits dd4hep/DDG4 imports.
All 12 dataset directories report installed despite the Geant4 ~data variant.
A C++ smoke program compiles, links and runs against DDCore, DDG4 and Geant4,
obtaining a DD4hep Detector and a NIST silicon material. This is dependency
readiness, not nODD construction, event transport or full-simulation validation.

Both Spack full-source queries fail: neither source tree is staged. A stage
path returned by spack location -s is not proof of files. No source downloads,
shared package installation, concretization or external helper edits occurred.

## Skill behavior and warnings

The self-contained acts-spack skill includes a node registry, preflight,
workflow instructions and the C++ smoke fixture. AGENTS.md routes dependent
requests through the skill. Unknown nodes warn as unverified; missing files,
changed fingerprints and missing requested sources warn before dependent work.
Runtime availability and full source availability stay separate. Five isolated
preflight tests cover these cases; actual source-mode preflight exits 2 with
warnings on this node. No other nodes were guessed or remotely inspected.

## Checks and corrections

Actual commands/results are recorded in the paired JSON. The sandbox denied
sysctl CPU detection; authorized fresh-shell execution removed that restriction.
The direct DD4hep import failure was resolved with its runtime setup script.
Skill validation used already installed Spack Python/PyYAML after system Python
lacked PyYAML. CMake warnings were not suppressed: the CLHEP view and original
config file resolve identically, and compile/link/run passed.

## Outcome and remaining work

The personal skill and repository copy match. The registry records the one
verified node, tested capabilities and unavailable full sources. Shared external
configuration was not copied or published. Source acquisition and a full-simulation
exercise remain separate tasks. No detector design, approval or held tracker
placement proposal was changed.

The first dashboard suite exposed a fixture omission: its synthetic checkouts
did not copy the new skills/ evidence directory (6 failures, 9 errors). The
fixture now includes that directory; assertions and tolerances are unchanged.

All 26 dashboard tests passed after the fixture correction; together with 15
logging/document-link tests and 5 preflight tests, 46 local tests pass. Published
[PR #16](https://github.com/asalzburger/nodd/pull/16), Software: Add node-aware
ACTS Spack workflow skill, at c092a1b94c4dd006c17dda510a2c9b78af0b2e60 with
review requested from asalzburger-review. This final metadata update changes no
skill/runtime evidence. GitHub CI was in progress at collection; no human approval
is inferred.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **6,311,031 input** and **24,628 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
