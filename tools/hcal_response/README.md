# Standalone HCAL with physical narrow sector-edge cassettes

The [current combined r–z overview](../../docs/layouts/figures/LAYOUT-002-DES046-rz.png)
shows tracker sensitive bounds, conditional solenoid, selected LAr ECAL and this
deep HCAL. [Named inputs and reproduction](../../docs/layouts/README.md) use
`draw_rz.py`; `--capture` checks the HCAL validation hashes and reconstructs the
selected ECAL envelopes including local services. Replaying its JSON requires
only Python; PNG/PDF conversion uses the existing `rsvg-convert` installation.

The isolated [DES046 prototype](../../docs/design/DES-046-hcal-sector-edge-coverage.md)
amends the DES045 barrel edge packing. The maintained tracker+ECAL exporter is
unchanged. Earlier DES036–045 data, sources and plots remain dated controls;
reproducing their exact geometry requires their recorded Git source revision.

The stack/envelopes stay at60×(30mmSteel235+12mmcarrier+1mmallowance)+10mmrear
cover:2590mm depth and1800mmsteel. Barrel apothems3130/5720mm, halfz6260mm;
endcaps |z|6760–9350mm, inner/outer apothems300/5710mm are unchanged.

The barrel now packs178224 original common carriers and90240 new edge cassettes.
Endcaps retain110880 common carriers. Across379344 physical carriers there are
23157216 tile channels. The100 edge widths are newly manufactured32–305.574485mm
units with one/two narrow PCBs, six tile rows and1–10 tangential columns. Actual
x-pitch is15.856633–29.990774mm; y-pitch remains30mm. Every core has its actual
reflector/recess/SiPM/LED, PCB/contact/ASIC, skin, coldplate and Ti/water cooling.
The old common unit0 is unchanged; no original boards/tiles are clipped.

The2mm continuous aluminium guide supersedes the20mm rail and its unqualified
load-path assumption. Steel extends to the guide. At each outer core plane the
inactive per-side tangent strip is7.047825mm, including seam, guide, fit, board
border and taper. The exact mechanical seam remains. Axial collector strips,
common-board gaps, barrel/endcap transition and external services remain real.

The descriptor preserves bits0–41 and appends `unit:8` at42–49. System13 denotes
barrel/side0; system14 denotes endcaps/sides1,2. Sector/layer/carrier locate an
assembly; the compound active child supplies its unit exactly once. Module and
sensor address actual sparse channels in that physical unit. Unit0 uses the
original two6×6 maps; new units use explicit centres/dimensions. Every union
keeps the exact disjoint recessed cores, identity-left Boolean construction and
first-core anchor. Raw context count is379344, not the23million logical cells.

```sh
python3 -B tools/hcal_response/export.py --output build/hcal50-edge/geometry
python3 -B -m unittest discover -s tools/hcal_response -p 'test_*.py' -v
software/env/run.sh cmake -S prototypes/hcal_response -B build/hcal50-edge/factories -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build build/hcal50-edge/factories --parallel 3
software/env/run.sh python3 -B tools/hcal_response/native.py \
  --directory build/hcal50-edge/geometry \
  --library build/hcal50-edge/factories/libnODDHCALResponsePrototype.dylib \
  --output build/hcal50-edge/native.json
```

Use the actual platform library suffix. The source-bound native audit checks
all unit parts/cores/IDs, overlaps, material/depth and sensitive rays. The actual
Geant4 conversion has its own source-domain gate before workers. Native runtime
checks use the reverified existing acts-spack environment; no dependencies are
installed. See the [prospective sample protocol](../../docs/validation/hcal50-edge/protocol.md)
and [execution/analysis source](../../software/analysis/hcal_response/README.md).
All XML, placements, full manifests, event/ROOT data and bulky logs stay local
under ignored build/. No optical, electronics or calibrated shower response is
implied by the raw deposited-energy simulation. Structural/thermal/hydraulic,
connector, radiation and whole-detector integration qualification remain open.
