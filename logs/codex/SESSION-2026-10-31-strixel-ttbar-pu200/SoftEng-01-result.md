# TTBAR-PU200-SoftEng-01

Curated read-only handoff from `/root/ttbar_native`. Input revision
`a734cf0d718846af84f919575725b9c7f0eee731`; implementation freeze
`aacf2ba0ab6c42e675959a8cb25c43c0ba7b477f`. Explicit SoftEng mandate applied;
native profile loading not claimed.

Owned runtime.py/test_runtime.py and StrixelPileup CMakeLists/PythiaBinding/
PileupAudit. Implemented isolated shared-sample generation/transport and four
response variants; full native gzipJSON replay including signed zero. Full
generated truth stays separate from guide-selected transport inputs. Audits
retain initial positions/time, authoritative origins, measurements/associations,
measured pixel space points, seeds/hypotheses, CKF and ambiguity candidates.
This historical handoff used the then-frozen ±15 mm window; later amendments
are outside its scope.

Matching clean ACTS355ea runtime: Python3.14.5, ROOT6.40.04, Pythia8.317,
SafeFatras; task-owned module built with AppleClang21, CMake4.4.4 and installed
pybind11 3.0.4/ABI11. Registry preflight unverified; actual build/runtime checked.
Shared dependencies and frozen helpers preserved.

- 13 runtime/adverse tests pass.
- Seed153043 one-event generation47.376s:24908generated,7586selected,
  8364simulated,59624hits,201converted primary vertices.
- Four smokes52.26–52.55s/case, peakRSS6.11–6.20GB; complete native roundtrip
  and strict ambiguity convergence maximumshared2.
- Final committed baseline54.918s/21.343ssequencer, peakRSS6210174976bytes;
  all source/native/prepared/sample hashes pass. Scientific audits byte-identical
  to preceding baseline. Report SHA256
  `79526610a0bc5e841ffe221ec3cfb58945b625a95d4282d836c18cd4fd5bd362`.
- `git diff --check` passes. Failed development attempts preserved.

Controls: build/strixel-ttbar-smoke/sample2,reco05stable,reco1,reco15,reco2,
reco05committed. Unchecked Pythia success was identified and corrected under
subsequent SoftEng-03 before production. No publication/shared modifications
or commits under this assignment. Exact token counters unavailable. This
handoff assembled from historical evidence without touching running production.
