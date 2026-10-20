# Si-W external service allocations (DES034)

DRAFT / PROTOTYPE. This standard-library study allocates empty external routing,
rear HCAL breaks and a prospective FCal region. It retains the Si-W components
from PR70/71 and changes only the selected candidate's rough HCAL outline.

```sh
python3 -B tools/siw_services/study.py
python3 -B tools/siw_services/study.py --check
python3 -B -m unittest discover -s tools/siw_services -p 'test_*.py' -v
python3 -B tools/layout_overview/draw.py
python3 -B tools/layout_overview/draw.py --check
rsvg-convert -o docs/layouts/figures/LAYOUT-001-rz.png docs/layouts/figures/LAYOUT-001-rz.svg
```

The report binds inputs and producer hashes. `--check` reproduces it and checks
HCAL/FCal values against the named layout inputs. Tests reject actual physical
clearance, packing and count failure modes. Existing rsvg-convert is optional
for preview; no new software dependency or detector plugin is added.

Source-count reconciliation, choice provenance, interfaces and limits are in
[DES034](../../docs/design/DES-034-siw-service-envelopes.md). Local cassette
ports/collectors and the full junction routing are missing; empty corridors
are not installed material or a hydraulic/throughput/thermal qualification.

Numeric output is serialized to nine decimal places in each labelled unit for
cross-platform libm portability. Physical checks remain unrounded; hashes and
serialized report replay are still exact.
