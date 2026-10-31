# SESSION-2026-10-31-reference-run-artifact-policy

The user instructed: “Ok, new rule also for PRs: do not check in big files from reference runs, only the resulting plots, if needed a binwise storage & the recipe to reproduce”. The earlier instruction to wait for a PR decision remains active. Started from5da4f6c with a clean working tree; exact task start and client usage are unavailable.

Recorded the standing policy in AGENTS.md, ADR-003, the PR template and the validation-report template. Git/PR contents should retain plots, the reproduction recipe and optional compact binwise data, with concise results/provenance. Large event samples, simulation/hit/track dumps, caches and bulkylogs stay local/ignored or in a maintainer-selected store. Binwise evidence documents bins/units/normalization/counts/denominators and needed uncertainty/correlation information; it does not disguise event-level data. Recipes include source/config/input identities, environment/dependencies, seeds and exact generation/analysis/plot commands. Clarify full-data versus compact-summary validation.

Policy applies to newly pushed history, not only final tree. Removing a file in a latercommit does not remove its blob; compression/chunking/LFS is not an automaticexception. Preserve evidence and existing authorization boundaries. No byte threshold was invented. ADR-003 remainsDRAFT: this explicituserinstruction does notapprove its widerenvironment/tolerance/storage-service proposals or scientificdesign. No physics/source/geometry change; no newprogress task or signoff.

Local documentation/governance checks are run before commit. No simulation rerun or newunit tests are needed for this policy-only update. No PRcreate/update, push, externalmessage or dataupload. Exact input/output/model/turn token counters unavailable; no estimate or private-state collection, usage empty.

All existing session/project/token-dashboard/workflow and diff validators pass. Newpolicy anchors/targets are present inallfourdocuments; ADRstatus remainsDRAFT. Sessionclosedwithpartialusagecoverage. Current changesremainlocalandPRpublicationheld.
