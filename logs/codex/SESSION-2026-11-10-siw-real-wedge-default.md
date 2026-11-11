# SESSION-2026-11-10-siw-real-wedge-default — Default LAYOUT-001 to reusable Si–W wedge volumes

## Scope and evidence

State collection method, available context, limitations, related IDs and starting
revision. Identify uncommitted user changes present before work.

## Selected conversation

Attribute requests to the user and outcomes to the assistant. Mark exact quotes
and paraphrases explicitly. Include corrections and changes in direction.
Exclude private model state, confidential content, and irrelevant system context.

## Decisions and outcomes

State rationale, alternatives, consequences and what remains unresolved. Never
convert implementation authorization into human design sign-off.

## Commands and validation

Record relevant commands, actual exits/results, failed attempts and remedies.
Distinguish structural checks from detector acceptance.

## Changes and revision links

List changed files or refer to the paired JSON inventory. Result commits are
recorded only once they exist; Git history locates this record's enclosing commit.

## Token accounting

Record the client-provided per-turn usage source and import command, or state why
exact counters are unavailable. Report observed input/output sums and missing
coverage from `session_log.py summary`; empty usage means unknown, not zero.
Never copy raw client archives or private model state. Do not duplicate turns
across tasks or add cached/reasoning subsets to the input/output totals.

## Follow-up

List remaining work, missing measurements and any human review needed.

## Specialist assignment SIW-WEDGE-SYSARCH

SysArch read-only interface assessment at
`0bc37ca08fed0bd7b121d6eebd5794dd3b584877`. Inputs are DES-030, DES-031,
the ECAL integration contract, the Si–W component exporters and the
maintained baseline exporter. Owned paths are empty. Return physical,
material and ID interface risks plus concrete validation checks.

## Specialist assignment SIW-WEDGE-PHYSVAL

PhysVal read-only assessment at
`2bd57912350e9e88b1918e0221b205153545346e`. Inputs are the integration
contract, both Si–W factories, the shared placement and envelope helpers,
the containment regression and maintained baseline exporter. Owned paths
are empty. Return actionable equivalence or validation issues.

## Scope and findings

The user directed the maintained default to use the faster description
and requested a pull request. The dedicated branch starts at the PR #118
merge on main. LAYOUT-001 now requests the real wedge envelopes. The
standalone default, flat replica metadata and no-envelope factory path
preserve the component audit and earlier compact contracts.

SysArch confirmed the 29.50 mm barrel–endcap envelope gap and 71.95 mm
endcap aperture clearance to the beam pipe. The tracker truth envelope
alone does not establish passive-service clearance. The independent
assessment called for the full native overlap scan and a separate
DD4hep `VolumeManager` lookup check.

PhysVal reviewed `2bd57912350e9e88b1918e0221b205153545346e` and independently
compared the fresh and stock LAYOUT-001 compacts. Removing the two
envelopes restores the complete stock ECAL detector subtrees, including
all 2,352 replica declarations. Materials and readouts agree exactly.
The review identified Geant4 step partitioning as a limit on inferring
shower equivalence from material and ID checks.

The Spack fingerprints changed since registry recording. Fresh imports
and dataset inspection verified the existing DD4hep, DDG4, ROOT, podio,
EDM4hep and Geant4 runtime. The full export, CMake builds, 33 hardware
tests, five composition tests, all 531,936 ECAL touchable and native
lookup checks and 65 material rays passed. The ECAL-only map build took
23.018 seconds. The maintained tracker-plus-ECAL overlap and transport
checks are recorded separately when they finish.

See the [validation recipe](../../docs/validation/siw-real-wedge-default/README.md).
Exact counters for the active turn and specialist turns were unavailable.

## Completed integration checks and draft

The full tracker-plus-ECAL native scan at 10 nm reports all ten systems,
13,506,078 physical nodes and zero overlaps or extrusions from
1,866,412 candidates. The process exited normally. The three integrated
Geant4 smoke events persisted and passed truth and hit-ID readback with
the initialized field at zero. Each event's aimed region carried the
dominant ECAL signal. The comparison includes actual native DD4hep
context, pad-bit mask, position and orientation checks for all ECAL sensors.

A negative native control perturbed one replica by 1 mm. The factory
reported the inconsistent transform and DD4hep terminated construction.
The software inventory and project records validate locally.

Draft PR #129 carries the requested default and the scoped validation
evidence. The initial hosted build failed on the session's relative link
to its validation report. The path is corrected in the closing update.
The science implementation is the reviewed and executed commit
`2bd57912350e9e88b1918e0221b205153545346e`. Exact active-turn counters
were unavailable.

## 2026-11-11 accounting correction and publication

Exact closed-turn usage is now recorded from the [PR129 recovery inventory](../usage/USAGE-2026-11-11-pr129-siw-wedges.json), using matched app request/turn IDs and verified parent/child metadata. Earlier statements that counters were unavailable describe the active-turn observation at the time. No counters are estimated or shared between canonical owners. The active merge-readiness turn and other-device/reviewer-task history remain excluded.
