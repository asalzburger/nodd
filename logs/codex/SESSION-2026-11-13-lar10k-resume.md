# SESSION-2026-11-13-lar10k-resume — matched electron comparison

User: “Now #139 is merged, please continue with the 10k electron sample comparing ALLIGRO to Si-W”.

Resumed preserved comparison branch after committing its deferred metadata and
ordinary-merging main, including PR139 mergef68cef1f949d941fc7f67c74357ab99059be0345.
Tracking conflict reconciled by stable IDs preserving both contributions. Source
for bounded assignments5ef3db386436f063f944d36e784ad918e176cd0f. Prototype only.
No unrelated worktrees changed. Earlier failed pilot5 retained untouched.

Used nodd-coordinate/nodd-review-validation and acts-spack. Preflight returned2
for setup/lock fingerprint drift; actual DD4hep1.38,Geant411.4.3,ROOT6.40.04 and
EDM4hep/podio imports plus all12datasets verified by SoftEng before native work.
No installations changed. Pure plotting Python is the existing ACTS venv,
NumPy2.5.4/Matplotlib3.11.2 imports verified; default Python lacks Matplotlib.

PhysVal assessed protocol/statistics at5ef3db3 and independently verified both
retained SiW comparator ledgers/worker policies. It found a missing explicit
detector/transport-policy selection guard; coordinator added fail-closed checks
for collections, worker populations, physics/cuts/field/RNG/active steps and raw
ROOT hash. All5comparison controls pass. Prospective raw widths are descriptive,
not fixed-energy intrinsic resolution. Final result assessment remains pending.

Parent usage remains active and excluded; child observations captured when closed.
Full payloads remain ignored locally.

## Assignments recorded before dispatch

```json
{
  "id": "LAR10K-RESUME-SoftEng",
  "role": "SoftEng",
  "input_revision": "5ef3db386436f063f944d36e784ad918e176cd0f",
  "inputs": [
    "docs/validation/lar10k/protocol.md",
    "software/analysis/lar_response/transport.py",
    "software/analysis/lar_response/Audit.cpp",
    "software/analysis/lar_response/steering.py",
    "software/analysis/lar_response/compare.py",
    "tools/lar_calorimeter/placement_steering.py"
  ],
  "mode": "write",
  "writable_paths": [
    "software/analysis/lar_response/transport.py",
    "software/analysis/lar_response/Audit.cpp",
    "software/analysis/lar_response/steering.py",
    "software/analysis/lar_response/test_transport.py",
    "software/analysis/lar_response/CMakeLists.txt"
  ],
  "task": "Resume full transport through successful10k generation/readback. Read repo AGENTS/PROJECT and acts-spack; reverify actual runtime. Fix prior first-hit MT nativeVolumeManager initialization race by serial preinitialization before workers, using validated placement steering pattern. Use merged maintained reusable period geometry (fresh export build/lar10k-resume/layout002), exact original10k primaries, existing unchanged PR138 LAr libraries by verified hashes or rebuild. Preserve failed pilot5 and old artifacts. Build/audit transport. Run serial/12worker24event matched controls,100event native-limit and5mm pilots then predeclared5mm12worker10000production and complete readback when controls pass. Use fresh dirs build/lar10k-resume. All ROOT/log/event payloads ignored; no physics/geometry retuning/install. You may commit ONLY owned code files for clean run provenance before production; notify coordinator before launch and return exact commands/paths/hashes. No other commits, PR publication or delegation. Persist through actual production/readback; report failures honestly.",
  "deliverable": "Working transport fixes, tests, exact executed receipts, successful10000event run/readback or concrete blocking evidence. Main owns analysis/report/PR/metadata.",
  "completion": "Production10000 unique primaries/hits and all12workers audited, pilot and serial/MT controls pass, or report explained failure without erasing evidence."
}
```
```json
{
  "id": "LAR10K-RESUME-PhysVal",
  "role": "PhysVal",
  "input_revision": "5ef3db386436f063f944d36e784ad918e176cd0f",
  "inputs": [
    "docs/validation/lar10k/protocol.md",
    "software/analysis/lar_response/transport.py",
    "software/analysis/lar_response/Audit.cpp",
    "software/analysis/lar_response/steering.py",
    "software/analysis/lar_response/compare.py",
    "software/analysis/lar_response/test_compare.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently review prospective matched10k comparison protocol and compare.py implementation before results. Read prior task context records and relevant DES. Verify exact retained SiW original/staggered comparator directories under ../nodd-ecal10k/build/ecal10k and build/ecal-staggering (read only), input identities and transport comparability. Inspect metadata guards, paired bootstrap/covariance/intervals, selection/zero tails and scientific claims. Run lightweight controls. No native simulation/writes/delegation. Return material findings and exact executable comparison CLI/paths.",
  "deliverable": "Revision-specific findings and comparator identity/commands, for coordinator journal. Later final result review separate.",
  "completion": "Prospective assumptions/analysis implementation assessed independently, concrete corrections reported with exact lines; no acceptance granted."
}
```

## Comparison contract review before dispatch

```json
{
  "id": "LAR10K-PhysVal-contract-review",
  "role": "PhysVal",
  "input_revision": "5adb79c2212d72e7841326dba85a1c4f5ae2f5e2",
  "inputs": [
    "software/analysis/lar_response/compare.py",
    "software/analysis/lar_response/test_compare.py",
    "docs/validation/lar10k/protocol.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review coordinator comparison-contract remediation against prior finding. Check wrong detector/native-limit pilot/worker/cut/seed/field/step/material and raw ROOT tampering fail-closed; primary hashes pinned to prospective sample. Run focused tests and optionally validate_contract on actual retained SiW originals/staggered (read-only; hashes require reading ROOT). No simulations/writes/delegation. Return remaining material gaps or bounded no-findings. Final LAr result review later.",
  "deliverable": "Revision-specific guard assessment and actual commands returned for session.",
  "completion": "Assess prior gap resolution without claiming response acceptance."
}
```
