# DES018 pixel-disc eta apertures

Isolated DRAFT prototype for [DES018](../../docs/design/DES-018-pixel-disc-eta-apertures.md).
It reads the frozen merged PR42 / DES017 layouts and writes a separate removal
schedule and evidence. No production geometry or previous artifact is changed.

The human-selected scope is |eta|<=4, pT>=1GeV and the luminous z±150mm envelope;
the transverse±1mm box conservatively contains the old0..1mm fixture. Selection
uses an analytic continuous exclusion bound for uniform axial fields0..4T and
the first outward traversal. Every active corner at its actual z must be0.10mm
below that bound. Entire inner rings alone are removed; surviving IDs, placements,
polar axes and support heights are preserved. The next retained ring has explicit
reachable witnesses, including both1GeV charge signs in4T. Full-detector field,
material/secondary transport and lower-pT physics are outside this screen.

`study.py` retains the schedule, heterogeneous cooling/services, support checks,
all-pT/straight controls and matched finite-patch hit comparisons. `native_audit.py`
compares native ACTS supporting-plane/RectangleBounds hits before/after and
exhaustive controls. Out-of-scope eta probes explicitly retain lost hits.
`report.py` produces the per-disc table, RZ and last-disc before/after figures,
overlap controls and artifact/producer hashes. Previous hermeticity, guard,
warm-thermal, service and engineering failures remain documented.

Use the existing NumPy/Shapely/Matplotlib environment from DES017; native checks
require the verified ACTS runtime and finite sensitivity binding. On the authorized
node read/run the acts-spack preflight, then `acts run acts-nodd` in the same shell
and activate its installed Python environment. No shared package changes needed.

```sh
python -B -m unittest discover -s tools/pixel_disc_eta_apertures -p 'test_*.py' -v
python -B tools/pixel_disc_eta_apertures/study.py --output build/disc-eta-apertures/run
python -B tools/pixel_disc_eta_apertures/native_audit.py \
  --run build/disc-eta-apertures/run --output build/disc-eta-apertures/native \
  --acts-source /path/to/verified/acts-source
MPLCONFIGDIR=build/disc-eta-apertures/matplotlib python -B tools/pixel_disc_eta_apertures/report.py \
  --run build/disc-eta-apertures/run --native build/disc-eta-apertures/native \
  --output build/disc-eta-apertures/report
```

The retained [report](../../docs/validation/DES-018/results.md) records the actual
source execution at PR42 merge plus dirty producer/input hashes. The selection
is maximal within the unchanged contiguous-ring catalogue, not a global tiling
optimum. Original support radii and plate remain; no full support mass saving,
hydraulic solution, CAD qualification or design sign-off follows from deletion.
