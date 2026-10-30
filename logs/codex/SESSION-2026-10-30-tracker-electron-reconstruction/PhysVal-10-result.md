# SPECIES-PhysVal-10 — Final retained integration

Separate read-only technical assessment at
157994cbcbc2ec3551dc6bcbad51b3fc9c0a212e. Agent
`/root/reco_species_physval`, thread 01a18c6e-900f-71a0-a297-68e56d22a87b.
No new blocking finding, canonical file changes or human acceptance.

All 130 manifest entries match pinned Git and working bytes. All 16 summary
files decompress to the independently reviewed analysis bytes; every NPZ is
byte-identical, with event vectors exactly 0…4999. All native reports and twelve
Geant4 mappings match execution evidence. The original eight Fatras muon
summary/NPZ files equal their aae2626 reference bytes. ROOT evidence covers the
exact matrix and binds all ROOT output hashes to native reports. Its producer
and source correctly identify 4670659, preceding the presentation amendment.

Retained species verification exits 0 for all 80,000 new events. The assessment
reuses PhysVal07/08/09 independent native classifications and actual ROOT checks;
it does not rescore the large raw streams. All twenty population/pT retained
statistics are checked independently: counts, finite pull moments/quantiles/
extrema/tails, all-eta and central resolutions, and hit coverage agree. All 120
six-parameter pull distributions normalize to the full finite denominator;
visible-range overflow is retained rather than renormalized away.

A fresh temporary replay reproduces performance.json and results.md exactly,
all thirty PNGs and four tail JSON files byte-for-byte. All thirty PDFs match
after removing only CreationDate metadata. The earlier ignored finalizer receipt
covers initial report/figure production and ROOT audits; this fresh replay binds
the final presentation source. Four full-pull overlays and both combined
comparison figures are inspected, including their six actual PDFs rendered
with Poppler. Momentum overlays, signs, labels, legends, full-tail/time-prior
caveats and separate population denominators are readable and correct.

The computed Geant4 electron100 warning and frozen muon-selected/no retuning
statement agree with the data. Electron momentum/charge failures, narrow
uncalibrated pull cores, mixed-candidate/secondary matching, Gaussian response,
one-way electron hypothesis, material differences and 25 ns time-cut limitations
remain explicit. Two Fatras electron5 transport failures stay in the denominator.
No repeat native simulation/build, full covariance LLT or Geant4-internal FPE
coverage is claimed by this integration assessment.

Actual commands: pinned git-show/hash/file-set comparisons; isolated Python
species_evidence.py verify, species_report.py and species_plot.py to temporary
outputs; NumPy/JSON/gzip comparisons; Poppler pdftoppm and original-resolution
image inspection. All completed checks pass. Temporary diagnostic receipt SHA:
2280597fb7670198b5eb04b5316163662b95c127e2b98c8bebaa74aee443fc5d.

Recommendation: retain this evidence as technically consistent at the exact pin.
DES041 remains DRAFT / isolated PROTOTYPE, requiring human expert acceptance.
