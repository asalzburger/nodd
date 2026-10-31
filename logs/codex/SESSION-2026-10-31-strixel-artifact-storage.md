# SESSION-2026-10-31-strixel-artifact-storage

The user asked: “What’s the disc space it needed ? Do not add those files to the PR, only the plots.” This bounded task starts at15da21c7cc2e3e6fea72b957db087caca9845ce0, with no unrelated changes. Exact start/client usage unavailable.

Measured retained ttbar workspace:18,564,907,008allocatedbytes=17.3GiB(18.6GB), excluding shareddependencies/runtime andsharedGitstorage. Successful sample+fourreconstructions9.25GiB; portableaudit1.47GiB; remainderfailedruns/smokes/builds/tmpdiagnostics. SixPNG/PDFpairs1,728,512bytes=1.65MiB. Unpublished Git blobs before cleanup occupy1,547,130,474packedbytes(~1.44GiB), including theGBTS follow-up; archivedcopiesremain local, so this is not a disk-space reclamation claim. Full breakdown in docs/validation/DES-042/local-artifacts.json.

Publication scope: only plots as generated output, with compact reports/provenance and rerun code. All674DES042NPZ/compressed/CSVfiles stay byte-identical locally and become ignored. Existingpublishedtruthdata are removed from the proposed filetree without rewriting publishedhistory. Original fullhistory preserved at refs/local-archives/strixel-pitch-study-with-data-2026-10-31 ->15da21c. Consolidate only the unpublished data-bearing tail after6bc69e1, preserving pinned8c451nativevalidator history. RemoteGitHubbranch confirmedaa9b0e7 via connector; no PR found. SSHreadfailed sandboxDNS; no remote mutation or forcepush.

Scientific native/matching/statistical/plot source bytes and all figures remain unchanged. Truth report renderer changes publication prose/local links only; deterministic numeric report check passes. Small figure-only verifier checks fourpublishedfamilies, pairedPNG/PDF inventories, path safety, hashes and source bindings; it additionally checks local profile hashes when those inputs exist. CI keeps synthetic analysis tests and this published-output check. Full event/bootstrap/bridge/root/replot verification remains an explicitlocal workflow because the user excludes its data. This is a publication-policy adaptation, not a claim of full data replay in CI.

New checker initially reached missing-pair rejection before unsafe-name validation; changed it to validate all paths first. Final56GBTS+66ttbarunit tests pass. No test relaxed. A data-absent checkout and finalvalidators remain to be checked before closure. No scientific design/sign-off change.

Exact input/output/model/turn token counters are unavailable; no estimate/private-state recovery. Usage remains empty.

The precommit guard caught four Gaussian-control event arrays not covered by the initial explicit ignores. Replaced the extension policy with recursive DES042 NPZ/compressedJSON/CSV rules; all674files are now explicitly checked ignored, absentfromindex andbyte-identical locally. The guard prevented their inclusion. Native/matching/statistics/plot sourcebytes and52GBTS/ttbarfigurefiles+2manifests match archived15da21c.
