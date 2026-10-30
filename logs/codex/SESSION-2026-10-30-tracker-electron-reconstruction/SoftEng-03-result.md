# SPECIES-SoftEng-03 — isolated Fatras numerical repair

Implemented only the five assigned new SafeFatras files; no running core source,
observer binary or shared dependency changed. Matching ACTS355ea source copies
are generated only inside task-owned build output, with six input hashes,
revision and pybind3.0.4/ABI11 guards. A distinct algorithm/interaction type and
hidden symbols avoid native symbol interposition. Runtime algorithm/logger name
remains FatrasSimulation, preserving the event RNG context.

The branch u>40 directly evaluates the exactly rounded energy-loss factor -1;
all gamma/four-angle random draws, multiplication order, photon generation,
particle update, selectors, interaction defaults, input/output aliases and
minimum momentum remain unchanged. No FPE check or mask changes.

Actual checks: build and ctest pass; 1,572,360 bitwise energy-loss comparisons
cover all finite binary64 exponents and threshold/extreme fixtures; 6,000 exact
original/safe parent, photon and RNG comparisons include an800X0 test slab.
Original libm underflow is a positive control; guarded hardware and ACTS FPE
controls pass. Python3.14.5 import and registered IAlgorithm ABI pass.
`nm -gU` exports only PyInit_nodd_safe_fatras.

Built module SHA256:
`95e83263f8ca7dc0b26e6b40fcdbb2ab0e5c1890b16da7a5fb2f1b2f3c7035bb`.
Generated algorithm SHA256:
`c10c5c3645b94f03117d6453914fac735024d0a55211144737a664434fbd6bae`.
Full native campaign replay and separate scientific assessment remain required.
