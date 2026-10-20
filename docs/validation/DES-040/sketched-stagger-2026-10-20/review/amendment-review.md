# SS-P2 — scope-label amendment addendum

Reviewed exact correction revision `1d9a49fee5651e41855bd5ad6fdb6adc475b0407` against original SS-P1 target `11ec9bb670bca2b882929d1d2b4ef7d9da534da6`, under the full prepared SS-P2 assignment. The original SS-P1 report, checker and structured result remain the scientific assessment. **SS-P1-F1 is resolved.** No additional scientific or material finding was identified.

The standard-library-only portable amendment checker passed. It read only exact Git objects and wrote only `/private/tmp/pr90-SS-P1-*`. The whole-repository tree difference is confined to the three assigned files plus the coordinator-owned session record and project tracker. In the scientific scope (797 files), 794 remain byte-identical; the three changed files are precisely README, validation JSON and the future validation module. All 80 other files under the dated artifact directory retain identical Git blob objects, including geometry, controls, NPZ directions/masks/distances, raw native events/inputs/corners, OBJ/MTL/ZIP, inventories and figures.

The future module changes exactly one literal sentence. The JSON changes only `limits[0]` and adds `metadata_amendment`; all other values are equal. The README is append-only and accurately explains the corrected scope and original acquisition identities. `geometric_bank` is the central mirrored bank; `full_sphere` is the full-4π iid bank. The correction does not imply new acquisition.

The canonical SHA-256 of all JSON fields other than `limits` and `metadata_amendment`, using UTF-8 `json.dumps(..., sort_keys=True, separators=(',', ':'))`, is identical before/after and matches the amendment:

`23af330273597f01e3643f8470e5e1a5903178c7b2fcc46e6a0b138d2783776b`.

The original validation JSON SHA-256 is correctly retained as `707725d59e5af9dc18c5c57c4ecf6950e1b5e01e1ce56b2ad9477383b7cf0eb1`; corrected JSON SHA-256 is `8545075d486e646b0668866f942eed769074c8caf36dede1afe425a50d5627b8`.

`source_revision` remains the actual execution freeze `65cf2741bd697ddb8c4022a751f275b41f63241e`. Each retained `source_sha256` matches its source at that freeze and the original reviewed revision. In particular, the actual executed module hash remains `3e5c7e281552bc1911a8945503144815f941701d60afc4f89d635c67ac5555a3`; the future, string-corrected module is `5cd884d086f69d71f54bfc1c355f1dcf2b541c2d862f1f7f2cc68d9be8e03e71`. Their distinction is factual and explicit.

Reproduce this bounded addendum:

```sh
python3 -B /private/tmp/pr90-SS-P1-amendment-check.py \
  --repo /Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout \
  --output /private/tmp/pr90-SS-P1-amendment-results.json
```

Actual result: `/private/tmp/pr90-SS-P1-amendment-results.json`; command output: `/private/tmp/pr90-SS-P1-amendment-run.log`. Checker SHA-256: `562ada0b096a47d37466ec614ce1185bdbca67d12302c0f8e7b6b3a6262dcbb6`. Runtime was ~0.30 s, Python 3.14.6. No full numerical or native scan, field solve, installed dependency work, repository edit or commit was performed. Scientific limitations and lack of engineering/human acceptance remain unchanged.
