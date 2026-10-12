# Pixel endcap local-support design screen

DRAFT / isolated PROTOTYPE, governed by [DES014](../../docs/design/DES-014-pixel-endcap-support.md).
It reads the selected PR34 layout and current PR35 barrel service evidence.
It never writes production geometry, compacts, ACTS material or a new baseline.
Proposal B changes only reported hypothetical module z/mounting faces.

```sh
MPLCONFIGDIR=/tmp/nodd-endcap-mpl python3 -B tools/pixel_endcap_support/report.py
python3 -B -m unittest discover -s tools/pixel_endcap_support -p 'test_*.py' -v
```

Requires Python 3.10+, NumPy and Matplotlib (existing project control dependencies).
No ACTS/DD4hep runtime is needed for these design screens. `--output /tmp/new-run`
keeps a future rerun separate from retained evidence. Outputs include five vector
SVG drawings, PNG previews, one PDF book, module-placement comparison CSV,
screening JSON, results and an artifact hash inventory.

Reusable blocks:

- `model.py`: SHA-pinned input, common-template test, hypothetical assembly,
  OBB checks and service-envelope interfaces.
- `thermal.py`: power-conserving finite-volume pickup-sheet solve, anisotropic
  and contact resistance model, heat/quality balance and sensitivities.
- `budget.py`: explicit component volumes, material normalization, beam brackets
  and accumulated current-barrel/endcap service demand.
- `drawings.py`: original dimensioned views from the same inputs.
- `report.py`: provenance, reproducible execution and review artifacts.

For a module/sensor update, first amend the design contract and update the source
path/SHA in `inputs.json`. The reader fails on an unexpected SHA. Review module
counts, occupied thickness, pickup dimensions, row parity, phi colouring, all
clearances and local-transport grouping; do not automatically keep old values.
Update pinned PR35 handoff evidence when barrel shapes/services change too.
Run into a fresh output directory and compare old/new reports before changing
retained evidence. Source/code hashes distinguish a changed working tree from
its base commit. Numerical checks passing is not design approval.

The current result has **no local module/pickup/foot overlaps**, but **fails the
thermal stress target and adverse trunk-capacity cases**. Tube transitions,
flex artwork, voltage drop, hydraulic stability, pressure certification, joint
FEA, material scans and coverage/ACTS validation remain unperformed. Thermal
control tests deliberately retain that failure; they must not be weakened to
produce a green design conclusion.

Issue #38 / DES015 PD-C11 supplies `placement.disc_abs_z_mm`: nine strictly increasing positive integer support datums. They are reflected on the negative end and replace, rather than add to, the legacy first-disc shift. Historical DES014 evidence retains its original inputs; [the position amendment](../../docs/validation/DES-015/issue38-disc-positions/results.md) compares against the previously implemented ±615.2 mm first datum.
