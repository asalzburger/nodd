# Python job steering

From the nODD repository root:

```sh
make geometry
make analysis
make material
make calorimeter-run CALORIMETER_MODE=edm4hep-jets
make calorimeter-analysis
```

The geometry job runs 128 straight tracks with seed 42; the default material job
records 8 geantino tracks in one event. Calorimeter controls use the retained
synthetic ActsExamples pipelines; select basic, jets, edm4hep or edm4hep-jets.
Scripts expose explicit build/input/output options. Make activates the node's
Spack runtime and the new ACTS build, with outputs under build/jobs.
Algorithms, adapters and event data remain in ../source; independent output
inspection remains in ../analysis. No job edits a dependency checkout.
