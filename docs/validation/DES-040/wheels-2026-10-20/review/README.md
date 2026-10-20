# Independent prototype assessments

[Source/input report](source-review.md) targets22a3f8c; [actual-artifact report](artifact-review.md)
targets0576b7a. Both state their planning overlap, executed checks and limitations.
The validator is a separate agent context, not a human engineering approver.
Reports and results were copied unchanged; scratch filenames in the original
execution records map to these retained portable scripts:

| Assessment | Script | Actual result |
|---|---|---|
| Source/input |[source-check.py](source-check.py)|[JSON](source-check.json)|
| Native events/counters/bounds |[native-artifact-check.py](native-artifact-check.py)|[JSON](native-artifact-check.json)|
| OBJ/ZIP/inventories/figures |[asset-check.py](asset-check.py)|[JSON](asset-check.json)|
| Generation document identity |[generation-document-proof.py](generation-document-proof.py)|[JSON](generation-document-proof.json)|

From the repository root, with Python and NumPy:

```sh
python3 -B docs/validation/DES-040/wheels-2026-10-20/review/native-artifact-check.py \
 --repo . --revision 0576b7a615c81d1687f0cf7a3ceb0ca310478481 --output /tmp/muon-native-check.json
python3 -B docs/validation/DES-040/wheels-2026-10-20/review/asset-check.py \
 --repo . --revision 0576b7a615c81d1687f0cf7a3ceb0ca310478481 --output /tmp/muon-assets-check.json
```

Native checking can optionally add `--raw-root reference/cache/pr90-wheels`
when the ignored original CSVs are available; the retained result records that
additional exact raw-payload audit. No native transport or energy solver is
rerun by these scripts. Immutable inputs come from `git show` at the named
revision. The generation-proof script writes its diagnostic companion files
beside itself; copy it to a temporary folder before rerunning it.
