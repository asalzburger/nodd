# Python job steering

Job configurations and execution entry points belong here. Keep algorithms in
`../source/ActsExamples` and inspect produced results in `../analysis`.


The maintained DD4hep default is now the PR104 balanced baseline; see
[its build, native validation and representation limits](../../docs/validation/DES-040-baseline/results.md).
The `nodd_truth_tracking.py` default campaign remains the explicitly frozen PR101
control and its PR100 material map. It must be run with its matching old compact.
For balanced performance, retain the DES040 candidate workflow and its transported
material/calibration inputs; do not attach the old map to the new compact by name.
The checked balanced payloads remain physically equivalent after maintained
source integration, with an ACTS ID permutation confined to the added disks.
No new Geant4 map or candidate-specific response campaign is implied.
