# TTBAR-PU200-PhysVal-07 — numerical criteria and sample reuse

Independent read-only assessment of original ACTS `355ea68493b326956756c9386d2fd9eaf9328568` arithmetic against project `250a211ff71be2ce7339cc043766f0d839470411`. No writes, builds or native reconstruction.

The stack alone does not identify the division: candidate sites are endcap `(1+tau²)/tau²` at lines213–214 and innovation reciprocals at308/310. Actual predivision diagnostics are required before selecting a remedy.

A permissible minimal correction handles only the demonstrated exact singular/nonfinite case, with no epsilon floor, replacement cap, threshold tuning, mask or event removal. Original finite-path arithmetic/acceptance must remain bitwise identical. Capture affected event, node/layer IDs, slope/covariances/denominators/branch decisions under active per-event FPE monitoring. Compare original, unchanged renamed, diagnostic and guarded implementations on identical measured pixels, retaining ordered seed IDs and quality bits. Quantify changed updates/chains/seeds and downstream tracks/classifications across all100events. Rejected singular branches cannot be presumed behavior-equivalent. Preserve the validated sample and all failed outputs.

The dirty external-sample controller is appropriate: completed generation/output hashes, event count and seed are verified; its original generation revision and report SHA remain distinct from the fresh reconstruction freeze. All10campaign tests independently passed.

Reviewed dirty hashes:

- campaign.py: `9a722d62a3a4029820df8e821e295cc8bf1eb59e3d281cba38272bc832068cf3`
- test_campaign.py: `7e9650b0317e2803ac3dd4ae072054f07cb0a9101f17ccf37458c4576e4abf1f`
- original filter: `6fa5dc68793b8f54fb65d3d07badc33657e3c182e6c70d1ec65ab39793db9afa`

Exact diagnostic and guard review remains pending. Failed reconstruction outputs are not performance evidence; no human acceptance is granted.
