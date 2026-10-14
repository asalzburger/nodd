# nODD DD4hep/ACTS adapter

This local ActsExamples extension is migrated from the existing acts-nodd
checkout: its material recorder, full tracker Gen3 conversion, source identity
reporting and steering are retained. DD4hep geometry remains owned by
`../../detectors`; the ACTS submodule contains no nODD implementation.

`getNoddDetector()` loads the complete BeamPipe + Tracker compact. Native sensor
transforms, rectangular bounds, XYZ axes and readout identities remain preserved;
each chip and both paired strip faces stay separate. The native beryllium pipe
slab decorates its finite cylindrical portal, and silicon slabs decorate sensors.
Passive supports/services still require a dedicated material-mapping campaign.
No ODD material map is applied.

Gen3 containers are coaxial about the beam while sensors retain their tilts and
stereo angles. Try-all navigation preserves the existing correctness-first
baseline. `geometryReport()` supplies source IDs, centres, axes, bounds and volume
counts for the independent analysis. Navigation envelopes are software margins,
not physical material. Existing draft engineering/coverage limitations remain.

From the nODD repository root:

```sh
make software
make software-test
make geometry
make analysis
make material
```

`build/dd4hep/detector/tracker/tracker.xml` and all five factory libraries plus
components registries must exist; the Make targets build them. Python jobs live
in `software/running`. `getNoddDetector(build_dir=...)` also accepts a directly
configured standalone detector build directory. `gen3=False` retains DD4hep-only
material recording and explicit legacy pixel compact controls.

The extension is installed with ACTS into the task-owned `build/installed/python`
package. `software/env/acts-run.sh`, invoked after Spack activation, selects the
new build's package and libraries. It does not source or modify the acts-nodd
runtime/install helpers. MPL-2.0 source notices are retained in all copied files.
