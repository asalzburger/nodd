# Issue38 — pixel disc silicon optimization

User requested separate overlap/positioning PRs, fixed overlap at10%, authorized acts-nodd, resumed the stopped app session and required usage recovery. The positioning PR separately lists each disc movement.

Drafted DES016 before implementing the isolated study. Retained fixed RD53i active matrices and nominal annulus; searched polar and mixed Cartesian/inner-ring tilings. Selected328 singles,5 z levels,0.1mm unqualified sensor guard, slim periphery/body allowance. Every disc passes overall/annulus10% screens and conservative continuous on-axis vertex coverage. New radius≈212mm requires support/service redesign. Inherited0.5mm guard fails. No production compact or historical evidence changed.

Ran acts-nodd:324 matched tracks for candidate and actual preliminary baseline, plus6 exhaustive control tracks, with zero finite-intersection/ID mismatches. Binary/source hashes and existing ACTS working-tree changes retained; shared ACTS source/dependencies untouched. Preflight registry fingerprints stale; actual runtime reverified. A first attempt incorrectly replaced ACTS PYTHONPATH and failed imports; corrected by prepending the ignored local Shapely target.

Recomputed full module/chip/link/power-chain/cooling circuit counts and tube/cable envelopes. Heat decreases26.8%, but commands/chains, boundary overhang and reduced trunk area make every inherited packing scenario fail. This is a conditional geometric proposal, requiring readout/support/cooling/routing review before adoption. Figures/results and executable controls are retained in DES016; tracking records bounded study completion without design sign-off.

Shared token usage is recorded once on the positioning PR. The repository recovery tool is run for completed app turns; active final counters are deferred until closure. No raw conversation or private model state is logged.
