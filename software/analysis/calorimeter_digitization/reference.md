# Issue #117 — original-framework deterministic comparison

Status: capability prepared; **the full Key4hep/Marlin reference run has not
been executed in this environment**. The synthetic comparator test is software
utility validation, not independent digitizer validation. The runtime, its
immutable build identity and the resulting original-processor ROOT output
remain required inputs.

The native executable `nodd_silicon_reference` consumes the original ODD
`ddsim` file and a separately produced full-framework reference output. It
checks SHA-256 values, equal event counts, exact ordered unique run/event IDs,
unchanged retained SimHits and contributions, then accepted cell IDs and cell
energies. Both source and reference must retain a single `EventHeader` per
event. The deterministic control requires one SimHit per cell, pair statistics
and noise disabled, fixed gain, no dead cells, all contributions integrated and
the same MIP/range/threshold configuration. It compares energies and selection;
the native weighted time and original earliest-contribution time are different
contracts and are deliberately not compared.

## Verified original implementation and units

The preferred original framework path is the EDM4hep-native
`DigitiserSiliconMip` in
[`key4hep/k4RecCalorimeter@03b3676cecbdf85818f6de159ecf90ffe2482cec`](https://github.com/key4hep/k4RecCalorimeter/tree/03b3676cecbdf85818f6de159ecf90ffe2482cec/RecCaloDigi).
Its `include/BaseDigitiser.h`, `src/BaseDigitiser.cc`,
`include/DigitiserSiliconMip.h`, `src/DigitiserSiliconMip.cc` and `README.md`
were inspected for this recipe. The package records its MarlinReco ancestry.
This is the full independent Gaudi event algorithm; it must not be replaced
with nODD's isolated helper on the reference side.

The upstream component consumes deposited GeV and writes **MIP values** to
`edm4hep::CalorimeterHit::energy`. Do not run
`CellEnergyCalibratorSiliconMip` before this comparison; its shower-GeV output
has another meaning. The nODD adapter's deposit-equivalent GeV is divided by
the same configured MIP deposit energy before comparing. Key4hep uses ROOT
random numbers and nODD's reused kernel uses CLHEP: stochastic bitwise agreement
is not expected. Start with both random effects disabled.

The comparator also recognizes the original Marlin processor
`RealisticCaloDigiSilicon` at
`iLCSoft/MarlinReco@255967eb855ebbc8f75ebaac190b268b63332e8b`, but an LCIO
route requires an additional verified, lossless round trip preserving full
64-bit IDs, contribution energies/times/positions and EventHeader identity.
That bridge has not been supplied or tested; the EDM4hep-native route avoids it.

## Original Key4hep steering, not yet executed

Use a runtime actually containing the pinned `RecCaloDigi` plugin and compatible
Gaudi, k4FWCore, DD4hep, EDM4hep and podio. Record source revisions, local patches,
installed component identities, versions and commands. A generic Key4hep setup
does not establish that this recently added plugin is installed.

`BaseDigitiser` gets its cell encoding from a **named DD4hep string constant**,
not directly from the readout. The pinned ODD readouts have `layer` in their
encoding but do not define `GlobalCalorimeterReadoutID`. Supply a task-local
compact wrapper containing only two string constants and an include of the
unchanged original compact. The following is a proposed adapter, unexecuted
with GeoSvc here; it does not change volumes, materials or segmentation:

```xml
<lccdd>
  <define>
    <constant name="I117EcalBarrelID" type="string"
      value="system:8,barrel:3,module:4,stave:1,layer:6,slice:5,x:32:-16,y:-16"/>
    <constant name="I117EcalEndcapID" type="string"
      value="system:8,barrel:3,module:4,stave:1,layer:6,slice:5,x:32:-16,z:-16"/>
  </define>
  <include ref="/absolute/path/to/pinned/ODD/xml/OpenDataDetector.xml"/>
</lccdd>
```

These strings are copied from ODD
`d70556f33b1c36abdf101a07ad8cf57eb56fbdf1`,
`xml/detectors/CalorimeterECal.xml`, the two `readout/id` elements.
Verify the resolved strings and `layer` decoding before interpreting a run.
DD4hep documents string constants in its
[XML persistency manual](https://dd4hep.web.cern.ch/dd4hep/usermanuals/DD4hepManual/DD4hepManualch2.html).

Save the following as a local `reference_digi.py`. It reads the configuration
shown below; its component and property names come from the pinned original
source. `IOSvc` usage and `k4run` follow the
[official k4FWCore I/O guide](https://key4hep.github.io/key4hep-doc/main/how-tos/k4fwcore/doc/PodioInputOutput.html).
The guide specifies that omitting `CollectionNames` reads all inputs and
`keep *` preserves them in output, which is needed for the same-hit checks.

```python
import json
import os
from pathlib import Path
from Configurables import GeoSvc, UniqueIDGenSvc, DigitiserSiliconMip
from k4FWCore import ApplicationMgr, IOSvc

cfg = json.loads(Path(os.environ["I117_REFERENCE_CONFIG"]).read_text())
geo = GeoSvc("GeoSvc", detectors=[os.environ["I117_REFERENCE_COMPACT"]])
io = IOSvc("IOSvc")
io.Input = os.environ["I117_REFERENCE_INPUT"]
io.Output = os.environ["I117_REFERENCE_OUTPUT"]
io.OutputType = "ROOT"
io.outputCommands = ["keep *"]
algorithms = []
for index, names in enumerate(cfg["collections"]):
    algorithms.append(DigitiserSiliconMip(
        f"Issue117SiliconReference{index}",
        inputHitCollection=names["sim"],
        inputHeaderCollection=cfg["header_collection"],
        outputHitCollection=names["reference"],
        outputRelationCollection=names["reference"] + "Links",
        EncodingStringParameterName=names["encoding_constant"],
        CaloType="em", CaloID="ecal", CaloLayout=names["layout"],
        calibration_mip=cfg["mip_energy_GeV"],
        silicon_pairEnergy=0.0,
        elec_noise_mip=0.0,
        elec_range_mip=cfg["dynamic_range_MIP"],
        threshold=cfg["threshold_MIP"], thresholdUnit="MIP",
        miscalibration_uncorrel=0.0, miscalibration_correl=0.0,
        deadCell_fraction=0.0,
        integrationMethod="Standard",
        timingCorrectForPropagation=0, timingResolution=0.0,
        timingWindowMin=-1.0e30, timingWindowMax=1.0e30,
    ))
ApplicationMgr(
    TopAlg=algorithms, EvtSel="NONE", EvtMax=-1,
    ExtSvc=[io, geo, UniqueIDGenSvc("UniqueIDGenSvc")],
)
```

`timingCut=0` alone is insufficient: the inspected `standardIntegration`
method still applies the window. The wide numerical window above is a
deterministic test control. Verify every contribution lies inside it. Neither
that window nor these disabled effects are selected nODD operating parameters.

In that separately verified runtime, after setting the four task-specific
environment variables to absolute paths, the original-framework command is:

```sh
k4run /absolute/path/to/reference_digi.py
```

Retain the exact steering/configuration/wrapper hashes and original command
exit status locally. No success for this command is claimed here.

## Comparison configuration and execution

Create a JSON configuration. Replace the uppercase values below with measured
or recorded values before running; do not invent a runtime identity or source
revision. The MIP scale must match the frozen calibration used in both jobs.
`absolute_tolerance_MIP=1e-5` plus `relative_tolerance=5e-6` is a proposed
numerical float-summation/persistence control, fixed before looking at the
reference. It is not a detector physics tolerance. Reference and native float
accumulation can differ, particularly near threshold; keep those disagreements
visible and review their origin rather than relaxing a criterion after failure.

```json
{
  "mip_energy_GeV": "REPLACE_WITH_POSITIVE_FROZEN_CALIBRATION_NUMBER",
  "pair_energy_eV": 0,
  "noise_MIP": 0,
  "threshold_MIP": 0.6,
  "dynamic_range_MIP": 2500,
  "seed": 117,
  "reference_energy_unit": "MIP",
  "input_position_contract": "cell-centres",
  "timing_mode": "all contributions; energy comparison only",
  "absolute_tolerance_MIP": 0.00001,
  "relative_tolerance": 0.000005,
  "header_collection": "EventHeader",
  "collections": [
    {"sim": "ECalBarrelCollection", "reference": "I117EcalBarrelDigi",
     "encoding_constant": "I117EcalBarrelID", "layout": "barrel"},
    {"sim": "ECalEndcapCollection", "reference": "I117EcalEndcapDigi",
     "encoding_constant": "I117EcalEndcapID", "layout": "endcap"}
  ],
  "sha256_tool": "/usr/bin/shasum",
  "input_sha256": "REPLACE_WITH_64_LOWERCASE_HEX_DIGITS",
  "reference_sha256": "REPLACE_WITH_64_LOWERCASE_HEX_DIGITS",
  "reference_producer": {
    "kind": "original-framework",
    "repository": "key4hep/k4RecCalorimeter",
    "revision": "03b3676cecbdf85818f6de159ecf90ffe2482cec",
    "processor": "DigitiserSiliconMip",
    "runtime_identity": "REPLACE_WITH_VERIFIED_BUILD_CONTAINER_OR_RELEASE_IDENTITY",
    "steering_sha256": "REPLACE_WITH_64_LOWERCASE_HEX_DIGITS"
  }
}
```

The input and reference hashes are verified with the specified
`shasum -a 256 -- FILE` compatible tool, invoked without a shell. Fill the
reference output hash after the independent job finishes; the steering reads
only response/collection fields, so this does not alter the processor's inputs.
Keep the full executed steering and runtime evidence with the local datasets;
the manifest's producer identity is recorded provenance, not authenticated by
the comparator.

Build with the normal optional upstream-backend configuration, then run:

```sh
software/env/run.sh /path/to/build/EDM4hep/nodd_silicon_reference \
  /path/to/original-ddsim.root /path/to/full-key4hep-digi.root \
  /path/to/comparison.json /path/to/new-reference-summary.json \
  /path/to/build/nodd_marlin_silicon_backend
```

Exit code 0 means the deterministic comparison passed with at least one matched
cell; 2 means accepted-cell or energy mismatches; 1 means invalid inputs,
provenance, event correspondence or execution. Existing summary files are not
overwritten. Missing/wrong collections, duplicate SimHit cells, changed
contributions, lost high identifier bits and event reordering fail explicitly.

The summary contains total events, unique ordered event-ID count, input and
accepted-cell denominators, matched/missing/extra/energy-mismatch counts,
maximum absolute energy difference and a binwise residual histogram normalized
by the declared tolerance. Full event/ID/hit payloads remain in the hashed local
ROOT files. Only compact summaries, resulting plots and this recipe belong in
Git under ADR-003. A deterministic pass would not establish stochastic,
timing, pileup, radiation or shower-performance agreement.

## Utility checks actually run

The `CalorimeterSiliconReferenceUtility` CTest writes two synthetic ROOT events,
including an empty event and a cell ID above 32 bits. It checks a known
deterministic response and rejects changed output energy, event IDs,
simulation contributions, hashes and energy-unit declarations. Its expected
reference values are synthetic controls. **No original Key4hep or Marlin
processor is executed by this test.**
