#!/usr/bin/env python3
"""Execute the original Key4hep silicon processor on a synthetic I/O fixture.

Run in the installed Key4hep/Spack environment. All numerical values below are
software test fixtures, not detector response parameters or physics evidence.
The requested work directory must not already exist; retain it for diagnostics.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys


INPUT_NAMES = ("EventHeader", "SimCalorimeterHits", "CaloHitContributions")
HIGH_CELL_ID = (1 << 40) | 7
MIP_GEV = 1.0e-4


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def write_input(path):
    import edm4hep
    import podio
    from podio import root_io

    writer = root_io.Writer(str(path))
    for event_number in range(2):
        frame = podio.Frame()
        headers = edm4hep.EventHeaderCollection()
        header = headers.create()
        header.setRunNumber(123)
        header.setEventNumber(event_number)
        header.setTimeStamp(1000 + event_number)
        hits = edm4hep.SimCalorimeterHitCollection()
        contributions = edm4hep.CaloHitContributionCollection()
        if event_number == 0:
            # Two contributions test integration; the second cell is rejected.
            for cell_id, deposits in (
                (HIGH_CELL_ID, ((0.000125, 2.0), (0.000075, 4.0))),
                (HIGH_CELL_ID + 256, ((0.000025, 3.0),)),
            ):
                hit = hits.create()
                hit.setCellID(cell_id)
                hit.setEnergy(sum(energy for energy, _ in deposits))
                hit.setPosition(edm4hep.Vector3f(10.0, 20.0, 30.0))
                for energy, time in deposits:
                    contribution = contributions.create()
                    contribution.setEnergy(energy)
                    contribution.setTime(time)
                    contribution.setPDG(13)
                    contribution.setStepPosition(edm4hep.Vector3f(11.0, 21.0, 31.0))
                    hit.addToContributions(contribution)
        frame.put(headers, INPUT_NAMES[0])
        frame.put(hits, INPUT_NAMES[1])
        frame.put(contributions, INPUT_NAMES[2])
        writer.write_frame(frame, "events")
    writer.finish()


def write_geometry(work):
    # Minimal world-only geometry: no detector factory or transport is involved.
    installation = os.environ.get("DD4hepINSTALL")
    require(installation is not None, "Activated DD4hep installation is unavailable")
    compact = Path(installation) / "DDDetectors/compact"
    for name in ("elements.xml", "materials.xml"):
        source = compact / name
        require(source.is_file(), f"Installed DD4hep material source is missing: {source}")
        shutil.copyfile(source, work / name)
    (work / "compact.xml").write_text('''<lccdd>
  <info name="Key4hepInstallationFixture" title="Synthetic installation smoke" author="nODD" version="1" status="test fixture"/>
  <includes><gdmlFile ref="elements.xml"/><gdmlFile ref="materials.xml"/></includes>
  <define>
    <constant name="world_x" value="1000*mm"/>
    <constant name="world_y" value="1000*mm"/>
    <constant name="world_z" value="1000*mm"/>
    <constant name="InstallationSmokeEncoding" type="string" value="layer:8,cell:56"/>
  </define>
  <readouts/>
  <detectors/>
</lccdd>
''')


def write_steering(work):
    steering = f'''# Synthetic software fixture; execute the original Gaudi algorithm.
from Configurables import GeoSvc, UniqueIDGenSvc, DigitiserSiliconMip, EventDataSvc
from k4FWCore import ApplicationMgr, IOSvc

io = IOSvc("IOSvc")
io.Input = {str(work / "input.root")!r}
io.Output = {str(work / "output.root")!r}
io.OutputType = "ROOT"
io.CollectionNames = {list(INPUT_NAMES)!r}
io.outputCommands = ["keep *"]
geo = GeoSvc("GeoSvc", detectors=[{str(work / "compact.xml")!r}], EnableGeant4Geo=False)
digi = DigitiserSiliconMip(
    "InstallationSmokeSilicon",
    inputHitCollection="SimCalorimeterHits", inputHeaderCollection="EventHeader",
    outputHitCollection="SmokeDigiHits", outputRelationCollection="SmokeDigiLinks",
    EncodingStringParameterName="InstallationSmokeEncoding",
    calibration_mip={MIP_GEV!r}, silicon_pairEnergy=0.0,
    elec_noise_mip=0.0, elec_range_mip=2500.0,
    threshold=0.5, thresholdUnit="MIP",
    miscalibration_uncorrel=0.0, miscalibration_correl=0.0,
    deadCell_fraction=0.0, integrationMethod="Standard",
    timingCorrectForPropagation=0, timingResolution=0.0,
    timingWindowMin=-1.0e10, timingWindowMax=1.0e10,
)
ApplicationMgr(TopAlg=[digi], EvtSel="NONE", EvtMax=2,
               ExtSvc=[EventDataSvc("EventDataSvc"), geo, UniqueIDGenSvc("UniqueIDGenSvc")])
'''
    (work / "steering.py").write_text(steering)


def xyz(value):
    return tuple(float(getattr(value, axis)) for axis in ("x", "y", "z"))


def object_id(value):
    oid = value.getObjectID()
    return int(oid.collectionID), int(oid.index)


def contribution_snapshot(contribution):
    return (float(contribution.getEnergy()), float(contribution.getTime()),
            int(contribution.getPDG()), xyz(contribution.getStepPosition()))


def retained_snapshot(frame):
    return {
        "headers": [(int(h.getRunNumber()), int(h.getEventNumber()), int(h.getTimeStamp()))
                    for h in frame.get("EventHeader")],
        "hits": [(int(h.getCellID()), float(h.getEnergy()), xyz(h.getPosition()),
                  tuple(contribution_snapshot(c) for c in h.getContributions()))
                 for h in frame.get("SimCalorimeterHits")],
        "contributions": [contribution_snapshot(c) for c in frame.get("CaloHitContributions")],
    }


def verify(input_path, output_path):
    from podio import root_io

    inputs = root_io.Reader(str(input_path)).get("events")
    outputs = root_io.Reader(str(output_path)).get("events")
    require(len(inputs) == len(outputs) == 2, "Expected exactly two input/output events")
    input_cells = accepted_cells = rejected_cells = empty_events = 0
    max_residual = 0.0
    for index, (original, result) in enumerate(zip(inputs, outputs)):
        before = retained_snapshot(original)
        after = retained_snapshot(result)
        require(before == after, f"Retained input changed in event {index}")
        require(before["headers"] == [(123, index, 1000 + index)], "Event identity changed")
        hits = result.get("SimCalorimeterHits")
        digi = result.get("SmokeDigiHits")
        links = result.get("SmokeDigiLinks")
        input_cells += len(hits)
        if index == 1:
            require(len(hits) == len(digi) == len(links) == 0, "Empty event gained hits")
            empty_events += 1
            continue
        require(len(hits) == 2 and len(digi) == len(links) == 1,
                "Threshold selection or relation count is wrong")
        require(int(digi[0].getCellID()) == HIGH_CELL_ID, "High cell-ID bits changed")
        residual = abs(float(digi[0].getEnergy()) - 2.0)
        require(math.isfinite(residual) and residual <= 2.0e-6, "MIP-scale output differs from 2 MIP")
        require(float(digi[0].getTime()) == 2.0, "Original earliest-contribution timing differs")
        require(xyz(digi[0].getPosition()) == xyz(hits[0].getPosition()), "Hit position changed")
        require(object_id(links[0].getFrom()) == object_id(digi[0]), "Truth link source is wrong")
        require(object_id(links[0].getTo()) == object_id(hits[0]), "Truth link target is wrong")
        require(float(links[0].getWeight()) == 1.0, "Truth link weight is wrong")
        accepted_cells += len(digi)
        rejected_cells += len(hits) - len(digi)
        max_residual = max(max_residual, residual)
    return dict(events=2, input_cells=input_cells, accepted_cells=accepted_cells,
                rejected_cells=rejected_cells, empty_events=empty_events,
                maximum_absolute_energy_residual_MIP=max_residual,
                energy_tolerance_MIP=2.0e-6,
                checks=["original processor execution", "threshold selection", "MIP energy",
                        "64-bit cell ID", "event identity", "retained SimHits and contributions",
                        "truth links", "empty event", "earliest contribution time"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path)
    args = parser.parse_args()
    work = args.work.resolve()
    require(not work.exists(), f"Refusing to overwrite existing work directory: {work}")
    executable = shutil.which("k4run")
    require(executable is not None, "k4run is absent from the activated environment")
    work.mkdir(parents=True)
    write_input(work / "input.root")
    write_geometry(work)
    write_steering(work)
    command = [sys.executable, executable, str(work / "steering.py")]
    with (work / "k4run.log").open("w") as log:
        process = subprocess.run(command, cwd=work, stdout=log, stderr=subprocess.STDOUT, check=False)
    require(process.returncode == 0,
            f"Original processor failed with exit {process.returncode}; inspect {work / 'k4run.log'}")
    summary = verify(work / "input.root", work / "output.root")
    summary.update(status="passed", scope="synthetic original-processor installation smoke; no physics validation",
                   command=command, python=sys.executable, processor="DigitiserSiliconMip",
                   sha256={name: sha256(work / name) for name in
                           ("input.root", "output.root", "compact.xml", "elements.xml", "materials.xml", "steering.py")},
                   script_sha256=sha256(__file__))
    (work / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
