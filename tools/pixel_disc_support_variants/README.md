# DES017 disc support variants

Isolated DRAFT prototype for [DES017](../../docs/design/DES-017-pixel-disc-support-variants.md).
No production compact/configuration is written. Frozen DES016/014 artifacts remain unchanged.

`study.py` compares eight single rings with four single plus two quad rings,
retaining the first four nominal rings. It proposes two-face support, tests
body/pickup/stem/core-insert bounds, and budgets eight chip-row cooling tracks,
chains, links and the fixed service envelope. `native_audit.py` uses actual ACTS
supporting-plane propagation and finite bounds; expected acceptance misses remain
in the report. `report.py` refines the thermal sheet calculation and produces
dimensioned layout/support/mounting drawings and a diagnostic coverage-gap map.

Dependencies are NumPy, Shapely2.1.2 and Matplotlib; native auditing additionally
requires the ACTS Python runtime and its finite-plane sensitivity support.
Reuse [the existing dependency requirement](../pixel_disc_optimization/requirements.txt)
in an isolated environment. On the authorized local node, read/run the acts-spack
preflight and use `acts run acts-nodd` followed by its installed Python environment.
The retained native JSON records the actual installation, source revision and local patches.
Do not modify shared dependencies or the sister source to reproduce this tool.

From the repository root, in that verified environment:

```sh
python -B -m unittest discover -s tools/pixel_disc_support_variants -p 'test_*.py' -v
python -B tools/pixel_disc_support_variants/study.py --output build/disc-support-variants/run
python -B tools/pixel_disc_support_variants/native_audit.py \
  --run build/disc-support-variants/run --output build/disc-support-variants/native \
  --acts-source /path/to/verified/acts-source
MPLCONFIGDIR=build/disc-support-variants/matplotlib python -B tools/pixel_disc_support_variants/report.py \
  --run build/disc-support-variants/run --native build/disc-support-variants/native \
  --output build/disc-support-variants/report
```

The retained [DES017 report](../../docs/validation/DES-017/results.md) came from
`run-04`/`native-04`; producer/input hashes identify dirty source execution at
parent revision8e593e32a97acc36b9a7850e1dfabc11d2175180. The native oracle and
coverage mathematics are reused without changing the prior code/evidence.
The output includes both raw nominal and new placed modules. Negative-side
assemblies reflect z and reverse u, preserving the physical radial v convention.
IDs are unique within each variant/all18 discs. Retained inner module IDs survive;
replacement quad IDs are synthetic prototype identifiers, not a production migration.

Candidate ranking uses128-segment polygon circles; retained station area screens
use the frozen2048-segment bounds. The coverage raster is only a diagnostic.
Thermal results use0.25 mm sheets with0.125 mm controls, retaining the exploratory
0.5/1 mm sensitivity. `artifacts.json` hashes retained evidence and producers.

The drawing's port/clip/locator arrangements are proposals, not swept CAD.
Conditional small guards, original-annulus holes, warm thermal failures, fixed
trunk/flange packing, approximate inventories and missing pressure/laminate/FEA
qualification remain explicit. Logger completion does not grant design approval.
