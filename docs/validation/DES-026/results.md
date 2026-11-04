# DES-026 — Sizing and illustration evidence

Date: 2026-10-12. Status: DRAFT / PROTOTYPE. No production geometry or field.

Executed with the existing envelope plotting environment: Python3.14.6,
NumPy2.5.3, Matplotlib3.11.2. Exact reported versions and input/code hashes are in
[sizing.json](sizing.json) and [figure.json](figure.json). The execution revision
is main da5c469 with new prototype files present; enclosing publication commits
are distinct. No dependencies were installed.

Commands and outcomes:

- `python -B tools/solenoid_baseline/run.py`: baseline and historical 6.6 m
  control calculated. Baseline143.173758MJ, 4.772459m³, 1.558656m vessel radius.
- `python -B -m unittest discover -s tools/solenoid_baseline -p 'test_*.py' -v`:
  six controls passed, including an independently integrated long-solenoid limit.
- `python -B tools/solenoid_baseline/tracker_snapshot.py --expected .../expected.json`:
  45,646 sensors grouped into52 bounds; all69 resolved repository source/input
  hashes match. Original inventory SHA256 retained. Extraction does not rerun
  DES025's historical native validation or determine passive extrema.
- `MPLCONFIGDIR=/tmp/nodd-mpl python -B tools/solenoid_baseline/plot.py`:
  PNG/SVG rendered from committed calculation and tracker bounds, visually
  inspected; initial legend/title overlap corrected before delivery.

At fixed baseline dimensions, energies at24×96,48×192,96×384 quadrature are
143.174927,143.173758,143.173325MJ. Final relative change3.023×10⁻⁶ passes
5×10⁻⁴; root residual8.03×10⁻¹³ passes10⁻⁸. Convergence tests do not estimate
conductor/structural uncertainties. At |z|=3.6m the vacuum on-axis field is
1.57494T, despite the central3T target.

The original PR6 inner control is reproduced: cold length6.6m, vessel7.1m,
outer vessel1.559419m and energy132.576MJ (rounded). This confirms reuse of the
same source-energy model, while the new length follows the present tracker
reservation. Main-coil vacuum energy includes fringe space; iron, coupled
magnets and installed total/peak fields are absent.

No new DD4hep, Geant4, structural, thermal, conductor or quench execution is
claimed. The required engineering/interface checks remain listed in DES026.
