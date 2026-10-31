# TTBAR-PU200-PhysVal-05 — failure diagnosis

Independent read-only review by `/root/ttbar_physval` of exact
`1000edb212287c3638f96e3a0c2eec0a6292cb18`, matching ACTS355ea and the preserved
failed attempt. No files changed, native jobs launched or performance statistics
produced. All100 chunks were written, but the sample remains failed and unusable
for reconstruction: one unmasked FLTUND in pow, separate from six step failures.

## Numerical requirement

FpeSafeGammaDistribution.hpp100–107 checks the combined product log, then
evaluates pow separately. The power can underflow despite a normal final
product. SafeBetheHeitler consumes gamma only through a loss fraction exactly
zero for0≤u<2^-54. Therefore an isolated guard can preserve observable loss
without claiming identical internal gamma values.

Proposed branch after unchanged gamma/uniform/rejection draws: return0 if
finite nonnegativeuPlus1≤2^256 and logPow<-512. Its product bound
2^256 exp(-512)<2^-256 is far inside the zero-loss region. Document validated
native-libm rounding premise and test threshold neighbours. Required gates:

1. Original calculations outside the proven zero-loss branch.
2. Every RNG draw/rejection iteration and all4angular draws unchanged.
3. Bitwise loss/photon/parent/RNG comparisons, native underflow-positive
   controls and active FPE monitoring; fixture(4,.5,1023.5) is suitable.
4. Task-owned separately identified source/build, preserving frozen/shared code.
5. Full100-event same-seed native payload replay against preserved attempt;
   keep every transport loss. No masks/resampling/cut relaxation/event removal.
6. Separate exact-corrected-source and evidence assessment.

## Transport inventory

Direct selected-versus-simulated inventories in all6affected events show no
missing headline-eligible generated particle. Five generated omissions are
pileup below pT1GeV, with no retained simulated output or hits:

| Event | Generated ID | Species | Initial pT [GeV] |
|---:|---|---|---:|
|8|[149,0,1,0,0]|pi+|0.404776|
|31|[124,0,73,0,0]|pi+|0.499237|
|36|[68,52,457,0,0]|e+|0.533854|
|42|[16,20,280,0,0]|pi+|0.487791|
|93|[195,0,33,0,0]|K+|0.512550|

Event63 has no missing selected generated particle above transport threshold.
Logged failed[14,0,85,1,1] denotes a simulation secondary; exact initialpT is
unavailable. Related source[14,0,85,0,0] is a retained neutral pileup photon,
pT1.12431GeV, excluded from charged denominator.

Important source limitation: MultiParticleSimulation.hpp137–153 erases the
queued initialParticle before copying its nowinvalidated reference into
FailedParticle. Logged identities alone are unreliable. Five generated losses
above are independently established by input/output inventories; exact secondary
metadata needs a safe observational diagnostic. Parent withdrew preliminary
log-based eligibility claim when this was found. Missing low-p/secondary hits
can affect occupancy/seeding/fakes, so transport must not be called complete.

Evidence: raw sample.log, corresponding6eventchunks and native-fpe-diagnostic
SHA256dfaa2a45fe4ebf460136e27dbb72281fa87d29f85b9d7016c879af06d8a11e4f.
No correction validated or human acceptance granted by this assessment.
