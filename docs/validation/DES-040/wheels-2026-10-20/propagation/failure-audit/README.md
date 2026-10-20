# Supplemental native failure diagnosis

The primary scans retain one step-limit row each: before88059 (5 GeV,+e)
and after28149 (2.65 GeV,+e). These stay unfinished in all primary tables and
bounds. No primary data, maximum steps, mask or numerical gate is altered.

[Actual commands, status rows, final native steps and hashes](audit.json)
record five reruns per system: original settings, half maximum step, tenfold
tighter surface tolerance, tenfold tighter RK tolerance, and exhaustive
candidate search. Gzip files retain complete original hits, native root/step
audits, status rows and metadata, including unrounded coordinates/uint64 IDs;
`decompressed_sha256` checks their original bytes. Primaries are retained.

Original/exhaustive reproduce exactly; half-step and tighter surface tolerance
still reach20,000 steps. Before cycles through a supporting root at z11.25 m
and negative native corrections; after alternates overshoot/correction near
(4.26875,4.07162,−0.93201) m. This is numerical cycling, not proof of a physical
closed orbit. Tighter RK (1e−12 m versus1e−11 m) yields field-masked before
and completed after. It diagnoses sensitivity; these supplemental trajectories
are not substituted into primary coverage. The before physical continuation
remains unknown after reaching a masked stencil.

Each primary failure contributes at most1/230,880 (0.000433%) to the all-track
scan; individual sampling-bank/case bounds use their own denominators. Field
masking is a much larger limitation. The current numerical controls therefore
do not establish universal convergence of every generated trajectory.

Reproduce with the same native binary/prepared banks:

```sh
python3 -B tools/muon_layout/wheels_acts/failure_audit.py \
 --work-root reference/cache/pr90-wheels \
 --executable reference/cache/pr90-wheels/build/nodd-muon-wheels-propagate \
 --output docs/validation/DES-040/wheels-2026-10-20/propagation/failure-audit
```

The deterministic gzip artifacts and executed source/binary hashes allow an
independent audit. Source revision names the repository HEAD at diagnosis;
actual numerical source and diagnostic source hashes remain explicit.
