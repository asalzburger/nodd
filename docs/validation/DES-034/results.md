# DES034 - Si-W service and forward allocation checks

2026-10-14 - DRAFT / PROTOTYPE. Analytic empty-envelope/packing scope only.

The primary source catalogue pins Si-W PR70/71 and LAr comparison revisions.
Implementation follows the design scope committed at
62b8b35765ff55163c504e3d551f4366a536948b. Source choices and producer/input hashes
are retained in [allocations.json](allocations.json); no detector toolkit or new
external dependency is used. The proposal modifies the candidate outline, not
standalone ECAL construction or production geometry.

Executed standard-library commands:

```sh
python3 -B tools/siw_services/study.py
python3 -B tools/siw_services/study.py --check
python3 -B -m unittest discover -s tools/siw_services -p 'test_*.py' -v
python3 -B tools/layout_overview/draw.py
python3 -B tools/layout_overview/draw.py --check
```

Ten tests pass: eight negative controls plus two nominal consistency tests. They reject the 30 mm rear gap, treating polygon apothem as
corner radius, sector lane interference, the 700 mm adverse-data lane, failing
merged junction capacity, FCal intrusion into HCAL or the Si-W endcap and powered-interface double
counting. Exact report reproduction and HCAL/FCal layout correspondence pass.
The valid SVG and existing rsvg-convert PNG were regenerated and visually inspected.
All eleven primary Git-object SHA256 bindings were recomputed and matched.

The allocated 300 mm annulus has 23.049 mm clearance outside the largest Si-W
corner. Ordinary 900x150 mm lanes clear HCAL by 35.214 mm and sector edges by
21.986 mm. Merged 880x220 mm lanes clear them by 22.171/21.064 mm; the doubled-
link, 30% fill case needs 166,698 of 193,600 mm2. A single 50 mm jacket elbow
needs 245 of 400 mm axial space. Seventy centreline/sweep bound points stay
outside the unchanged ECAL and inside the reserved HCAL annulus/rear break.
These are conservative bounds and sampled elbow points, not a native union audit.

The FCal interval is 50 mm behind ECAL and 10 mm inside HCAL's minimum circular
aperture. It has no installed material or acceptance. The retained ECAL heat
hypotheses imply 259.452 kW and ideal 12.414 kg/s local water. External feed
copper/water examples and 7.190 kW power-loop loss remain planning estimates;
no thermal, hydraulic, cable, support, field or shower qualification is implied.

The separate SysArch input and frozen-proposal PhysVal assessment are curated in
the paired session record with exact revisions. No human sign-off is recorded.
Local cassette ports/collectors, balanced station wiring, bend/connector packing,
pressure drop, support loads, machine clearance and a qualified forward design
remain open. No DD4hep/Geant4, installed material or field/performance job was run.
