# DES-027 — Static source and hardware-reference inspection

Date: 2026-10-12. Status: DRAFT. Source inspection only.

Starting nODD main: da5c469f4d64a711c4f466cac79ff51e83244859. Its detector
CMake targets/configuration and tracker exporter contain beam pipe/tracker,
without a maintained nODD calorimeter assembly. This remains distinct from
ODD full-detector configurations and the ActsExamples reconstruction prototype.

Executed Python3.14.6 standard-library audit:

```sh
python3 -B tools/calorimeter_audit/audit.py --odd-dir "$odd_source_directory"
python3 -B -m unittest discover -s tools/calorimeter_audit -p 'test_*.py' -v
```

Both passed. All seven upstream input files match Git bytes at pinned
c167363f3d4ad1540a577af99071283caf54f3a6. Four arithmetic/accounting controls
passed. [odd-inventory.json](odd-inventory.json) records exact source and code
hashes, mixtures, readouts, dimensions, stack/material sums and derived bounds.

Results: ECAL48×5.05mm=242.4mm; HCAL36×51mm=1836mm. HCAL's PCB mixture totals
576mm with290.924g/cm² normal areal mass, of which238.198g/cm² is copper.
Barrel outer corner radii inferred from trapezoids are1.521638m and3.503315m;
endcap radius inputs use a different convention. Native containment is untested.

Public primary sources were checked: PR6 expert comments, pinned v6.0.2
ECAL/HCAL XML, CMS2025 HGCAL construction note and arXiv2401.02793v1 force
study. Local registered PDFs were read with bundled pypdf6.10.0: CMS-TDR-019
PDF58/63–65, ATLAS JINST PDF165–166 and ATLAS solenoid PDF1–2. Their local hashes
are checked against the catalogue at closeout; copyrighted PDFs are not copied.
CDS's browser challenge prevented direct web retrieval; existing registered
local copies supplied the required passages. No access restriction was bypassed.

No DD4hep/Geant4 runtime, mechanics, thermal circuit, power route or
calorimeter/jet/PF performance execution is claimed. The implementation gates
and unresolved inputs are explicit in DES027.
