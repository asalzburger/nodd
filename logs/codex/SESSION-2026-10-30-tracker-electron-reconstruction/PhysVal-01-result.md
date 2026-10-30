# RECO-SPECIES-PhysVal-01 — curated protocol assessment

Input aae262694535523b1e0fd968e4170b061429f0a6; separately read working DES
amendment SHA59975a4e1a538ca01d32c12e5d18ad068f4ff73445e4ab5e3044eadfa9870c44.
Matching clean ACTS355ea684 source. Read-only, no files or simulations changed.

Requires named gun/hypothesis consistency with actual PDG/mass/charge audit;
lepton signs differ from pion signs. Retain native Fatras electron-ionization
and ordering limitation and 0.5GeV absolute momentum cutoff. Electron finder is
multicomponent CKF with brems recovery (12 components, weight cutoff1e-4),
not a separate GaussianSumFitter refit. Keep all generated denominators, full
particle IDs and secondary categories, frozen matching, uncut residual/pull
tails and prior-dominated time. Existing muons are a population comparison.

Actual checks: exact revision source reads/hashes, working DES diff/hash, clean
ACTS source and native helper/hypothesis/physics/classifier source inspection.
Spack preflight unverified; no runtime or performance validation claimed.
Suitable bounded protocol with these checks; no human acceptance.
