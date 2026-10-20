# DES040 independent technical review

[V1 assessment](review.json) reviews scientific source and evidence at exact
commit `8e93a131aa5f6d186f27a1a050221d5be50d0633`. It found no blocking correction
within the isolated DRAFT prototype scope. This record does not accept the
coverage losses, certify mechanical construction or grant human design sign-off.
The review and publication records were added after the reviewed commit; the
scientific source and its generated results were not changed.

The reviewer ran all 21 new controls and the source/artifact check. Its
[independent spotchecks](independent-spotchecks.json) verified all 52 inherited
file hashes, checked all panel/support broad-phase pairs using separately derived
SAT, reconciled all 1,310 material contacts and the grounded 530-node graph, and
compared independently derived plane/depth arithmetic on 16,384 full-sphere rays.
Forty-seven of the full-volume coil certificates were recomputed; the existing
mask/certificate and material-wall decomposition are reused and disclosed.

The reviewer authored earlier planning/math checks and some inherited DES039
evidence; it did not author the implemented root/S1/S2 DES040 source. This is a
separate technical assessment, not a second solid-model engine or a statement of
human expertise. Detailed command results, authorship and limits remain in the
assessment.

The retained [read-only checker](independent-spotchecks.py) can be rerun against
the frozen source snapshot or the unchanged scientific files in this branch:

```sh
python3 -B docs/validation/DES-040/independent-spotchecks.py --root . --git-root . --output /tmp/des040-spotchecks.json
```

It writes only the explicit output. Results.json input hashes and the git-object
invariance checks guard the intended source/data scope. It does not rerun the
full packing, million-ray integral, union-mass integral, field map or energy solve.
