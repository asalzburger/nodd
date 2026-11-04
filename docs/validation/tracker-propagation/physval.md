# Separate scientific assessment

**Technical assessment, not human design approval.** Read-only PhysVal agent
assignments used the repository mandate and prepared prompts. No native role
loading, simulation rerun, dependency installation or independent expertise is
inferred from using a separate agent context.

## Final measured evidence

Assignment `TRKPROP-PhysVal-02` reviewed exactly
`5181bd317e6b369388805e1567d695a22a4e33aa` on 2026-10-23. It inspected pinned
retained data before author prose and used the isolated unrooted Python to
recompute profiles, hashes, native source counts and numerical diagnostics.
Supplementary native ROOT files were verified against committed run manifests
before inspection. The reviewer found **no remaining scientific blocker for the
requested prototype overview**, with the existing qualifications retained.

Actual independent checks:

- All 24,576 nominal probes have complete unique generated/summary/step identities,
  charged muons from the origin and requested transverse momentum verified from
  initial momentum components.
- All native final steps reach the outer World portal within 0.001 mm. Recorded
  maximum r=1111.327393 mm and |z|=4001 mm, plus 50 mm, fit the field-map support.
- All seven DD4hep source-system counts reproduce CSV rows and native
  `nSensitives`; no repeated sensitive IDs occur.
- All 33 profiles reproduce from compressed counts: means agree exactly and the
  largest standard-error difference is 1.95×10⁻¹⁵. Actual ROOT TProfiles and
  unrooted branch profiles also match. Per-bin populations are 79–131, including
  subsystem zero-crossing probes.
- The prior duplicate-probe adversarial fixture is rejected, generated kinematics
  and executed identities are checked, and declared field normalization is enforced.
- The reviewer visually inspected the hash-matched overview PNG.

The reviewer independently recovered exactly seven changed 1 GeV probes in the
finer-map control: events 4,48,167,259,356,398,421, each changing one sensitive in
pixel endcap systems 2/3 or short-strip endcap system 5. Four gains and three losses
give +1/512 in the full-tracker mean. The approximate local clearances change sign;
actual crossing-side positions lie inside the finite sensor bounds. Common
crossing shifts reproduce 0.029–0.066 mm. These support the finite-edge explanation.

**Per-track map convergence is not demonstrated.** The retained
`DIFFERENCES_REQUIRE_REVIEW` status is appropriate. Improved sampled field
interpolation error, 0.305→0.061 mT, does not bound errors at discontinuous sensor
edges. The review recommended adding 7/512=1.37% changed probes, mean absolute
change 7/512 and a largest affected control-bin shift of 0.2 crossings alongside
the signed mean, because gains/losses cancel. The coordinator incorporated that
clarification after this review without changing measured data or source code.
These are observations in 512 control probes, not bounds for all 8,192 nominal probes.

Half-step counts and refined-map 10/100 GeV counts are unchanged. Independent-seed
full-tracker means differ by 0.92,0.03,0.02 combined standard errors at 1/10/100 GeV.
Charge, eta-sign and phi splits are descriptive; no exact detector symmetry was
required. Precision acceptance work needs stronger map convergence, more control
statistics and paired-difference uncertainty treatment. Sensitive-plane counts
remain distinct from reconstructed measurements, efficiency and performance.

## Preliminary findings and resolution

Assignment `TRKPROP-PhysVal-01` reviewed exactly
`7b02e7eb88196d1dd0282e32a12a3d7b3db4dc5a`, before native implementation.
It confirmed the finite uniform-J sheet construction and population-profile
errors, independently reproducing central 3 T and analytic axis values 2.2193263 T
at 3 m and 1.5749351 T at 3.6 m. A ROOT/unrooted fixture with zero-inclusive counts
[0,2] and [0,4] yielded means [1,2] and mean variances [0.5,2].

It reported two P2 defects: row-count checks permitted duplicate IDs and invalid
kinematics, and declared field normalization could diverge from executed sizing.
The coordinator added expected-ID, pT/charge/phi, native-particle and configuration
checks, enforced source normalization, and added adversarial unit controls.
PhysVal02 explicitly verified these corrections. Sampled maxima remain labeled
as sampled checks; no global field accuracy or tracking acceptance is claimed.
