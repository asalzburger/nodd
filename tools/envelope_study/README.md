# Envelope study — DES-003

**PROTOTYPE, DRAFT:** allocation diagnostics for the unsigned global detector
proposal. This tool generates no DD4hep geometry and is not connected to detector
production. The envelope layout, interfaces and numerical acceptance requirements
remain subject to human review.

Input: [candidate allocations](../../docs/design/DES-003-envelopes.json).
Output: [descriptive report](../../docs/validation/DES-003-envelope-diagnostics.json)
and [r–z drawing](../../docs/design/figures/DES-003-envelope-rz.svg).

## Reproduce

Run from the repository root. Reporting and unit tests need only Python's standard
library; plotting uses the pinned dependencies in `requirements.txt`.
The recorded environment is Python **3.14.6**, Matplotlib **3.11.2** on macOS.
Dependency compatibility on other Python/platform versions has not been tested.

```sh
python3 -m venv reference/cache/envelope-venv
reference/cache/envelope-venv/bin/python -m pip install -r tools/envelope_study/requirements.txt
reference/cache/envelope-venv/bin/python -B -m unittest discover -s tools/envelope_study -p 'test_*.py'
MPLCONFIGDIR=/tmp/nodd-mpl XDG_CACHE_HOME=/tmp/nodd-cache reference/cache/envelope-venv/bin/python -B tools/envelope_study/study.py docs/design/DES-003-envelopes.json --report docs/validation/DES-003-envelope-diagnostics.json --figures docs/design/figures
```

The existing local environment can be reused; creation/installation is only needed
for a fresh setup. Network/package-installation permissions follow the local
execution policy. Generated environments and caches are ignored, not vendored.
Omit `--figures` to produce only the JSON report without plotting dependencies.

## Contract and interpretation

- Coordinates are in metres, with nonnegative positive-z rectangles and declared
  `z -> -z` reflection symmetry. Radial and axial intervals must have positive
  width, region IDs must be unique, and each allocation carries a proposed design
  choice and rationale.
- A ray starts at the origin, with radial direction `1/cosh(eta)` and longitudinal
  direction `tanh(abs(eta))`. Its path interval is the intersection of the two
  coordinate intervals. Stable expressions avoid overflow at very large η.
- Exact rectangle contact is not a positive-area overlap. Reported overlaps mean
  competing allocations, not necessarily overlapping constructed volumes.
- Ray tangencies within eight floating-point ULPs of the entry/exit distances are
  discarded. This numerical roundoff guard is not a physical clearance threshold.
- The report records ordered envelope crossings and path lengths, not sensitive
  layers, hit counts, efficiency, radiation lengths or interaction lengths.
- No azimuthal structure, displaced vertices, curved tracks, material, field or
  detector response is modelled. Sampled rays do not prove hermeticity.
- Guide rays on the drawing are positive finite pseudorapidities. Plot limits,
  colors and region labels come from the input; they are presentation settings.

Provenance records input/script hashes, Python and plotting versions, executed
command, source-study revision, project HEAD and whether the checkout was dirty.
HEAD is the pre-generation checkout identity, not a claim that generated files
already belonged to that commit. Hashes identify exact input/script bytes when
the checkout is dirty; regeneration after committing legitimately changes HEAD
metadata. Drawing byte identity across platforms/fonts is not guaranteed.

## Checks and further work

Tests use explicitly synthetic dimensions: transverse/diagonal rays, reflected
directions, forward holes, tangencies, allocation contact/overlap, invalid units,
nonfinite inputs, boolean coordinates and extreme η. These establish the small
analytic implementation, not detector performance.

The [software input](../../docs/design/inputs/DES-003-software-validation-input.md)
defines the later active-surface, material-scenario and actual transport checks.
Do not reinterpret the rectangles as those richer models without extending the
input contract and reviewing its physical assumptions.
