"""Native candidate construction with unchanged PR101 transport and fit chain."""
import copy
import gzip
import importlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT_DIR=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT_DIR/"software/analysis/gen3_material_mapping"))
sys.path.insert(0,str(ROOT_DIR/"software/analysis/truth_tracking"))
from material_runtime import native_imports,apply_saved_map,sha256,write_report
from export_geometry import build_export
from select_surfaces import select
from digitization import build_config,apply_variance_table
from runtime import root_inventory
from compact import export
from material import select_candidate,transport,remap_errors


def load_cli(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def prepare(args,variant):
    args.output.mkdir(parents=True,exist_ok=True)
    compact=args.output/"tracker.xml"
    compact_audit=export(args.compact,variant,compact)
    shutil.copyfile(args.compact.with_name("materials.xml"),args.output/"materials.xml")
    ROOT,acts,sidecar=native_imports(args.native_module_dir)
    from acts.examples.nodd import getNoddDetector
    sys.path.insert(0,str(args.observer_module_dir))
    observer=importlib.import_module("nodd_truth_tracking")
    sys.path.insert(0,str(args.material_module_dir))
    helper=importlib.import_module("nodd_tracker_material")
    detector=getNoddDetector(nodd_dir=args.nodd_dir,build_dir=args.build_dir,compact_file=compact,
                             logLevel=acts.logging.WARNING)
    geometry=detector.trackingGeometry();context=detector.nominalGeometryContext()
    report=json.loads(detector.geometryReport())
    converter=acts.json.TrackingGeometryJsonConverter(level=acts.logging.WARNING)
    native=json.loads(converter.toJson(context,geometry))
    exported=build_export(native,report,lambda x:acts.GeometryIdentifier(**(x or {})).value)
    del native
    baseline_geometry=json.loads((ROOT_DIR/"docs/validation/gen3-material-mapping/geometry-summary.json").read_text())
    source_manifest=json.loads(args.manifest.read_text())
    candidate_manifest=select_candidate(exported,source_manifest["configuration"],variant,select)
    source_map_path=ROOT_DIR/"docs/validation/gen3-material-map-run/material_map.json.gz"
    with gzip.open(source_map_path,"rt") as stream:source_map=json.load(stream)
    candidate_map,material_audit=transport(source_manifest,candidate_manifest,source_map,variant,helper,
                                          compact_audit["inventory_ratios"])
    write_report(args.output/"selection.json",candidate_manifest)
    write_report(args.output/"material-map.json",candidate_map)
    decoration=sidecar.configure(geometry,context,candidate_manifest["surfaces"])
    decoration.pop("surfaces")
    decoration.update(apply_saved_map(geometry,candidate_manifest,acts,args.output/"material-map.json",sidecar))
    source_campaign=ROOT_DIR/"software/analysis/truth_tracking/campaign.json"
    config=json.loads(source_campaign.read_text());config["seed"]=args.seed
    config["geometry"]="DES040 candidate "+variant["id"]
    donors={tuple(map(int,k.split(":"))):tuple(v) for k,v in compact_audit["calibration_donors"].items()}
    if args.digitization=="geometric":
        table_path=ROOT_DIR/config["error_training"]["error_table"]
        table=json.loads(table_path.read_text())
        errors=remap_errors(table,baseline_geometry,exported,donors)
        digi,counts=build_config(report["sensors"],config["digitization"])
        apply_variance_table(digi,errors)
    else:
        import smearing
        table_path=ROOT_DIR/"docs/validation/truth-tracking-baseline/smearing/pooled-widths.json"
        table=json.loads(table_path.read_text());errors=remap_errors(table,baseline_geometry,exported,donors,pooled=True)
        settings={"model":"gaussian_smearing","merge":False,"measured_coordinates_by_system":copy.deepcopy(smearing.COORDINATES)}
        digi,counts=smearing.build_config(report["sensors"],settings,errors)
        config["digitization"]=settings
    write_report(args.output/"error-table.json",errors)
    write_report(args.output/"digitization.json",digi)
    write_report(args.output/"campaign.json",config)
    no_op=None
    if compact.read_bytes()==args.compact.read_bytes():
        no_op={"compact_bytes_identical":True,"material_semantically_identical":candidate_map==source_map,
               "calibration_semantically_identical":errors==table}
        if not all(no_op.values()):raise RuntimeError("No-op candidate changed frozen material/calibration")
    # Keep the full audit for coverage/identifier comparison; it is study-local.
    write_report(args.output/"geometry.json",exported)
    files=[("source_material_map",source_map_path),("source_error_table",table_path),
        ("source_geometry",ROOT_DIR/"docs/validation/gen3-material-mapping/geometry-summary.json"),
        *[("candidate_input",args.output/name) for name in ("tracker.xml","materials.xml","selection.json","material-map.json","error-table.json","digitization.json","campaign.json")],
        ("material_helper",Path(helper.__file__)),("observer",Path(observer.__file__))]
    info={"compact_audit":compact_audit,"material_transport":material_audit,
        "native_decoration":decoration,"digitization_sensors_by_system":counts,
        "candidate_counts":exported["checks"],"source_error_table_sha256":sha256(table_path),"no_op_equivalence":no_op,
        "material_approximation":"Retained carrier effective profile relocated by complete logical role with area/count scaling; added donor-area-average homogeneous disk downstream; no new Geant4 mapping",
        "calibration_approximation":"Frozen PR101 errors remapped by physical system/layer; additional disks inherit named donor; no candidate retraining"}
    if args.digitization=="geometric":
        info["digitization_native_defaults"]={"model":"geometric","doMerge":True,"componentDigital":True,
            "post_cluster_errors":"Frozen PR101 RMS² by cluster size with native overflow clamp"}
    else:
        info["digitization_native_defaults"]={"model":"Gauss","doMerge":False,**smearing.native_boundary_contract(acts)}
    return ROOT,acts,sidecar,observer,helper,detector,geometry,config,info,files


def execute(args,config,ROOT,acts,detector,geometry,observer):
    if args.digitization=="geometric":
        baseline=load_cli("nodd_frozen_geometric_cli",ROOT_DIR/"software/running/nodd_truth_tracking.py")
        args.simulation="fatras";args.training=False;args.write_simhits=False
        args.error_table=args.output/"error-table.json";args.geant4_run_mode="persistent"
        baseline.run(args,config,ROOT,acts,detector,geometry,observer)
    else:
        baseline=load_cli("nodd_frozen_gaussian_cli",ROOT_DIR/"software/running/nodd_truth_tracking_smearing.py")
        baseline.run(args,config,acts,detector,geometry,observer)
    names=("particles.root","particles_selected.root","audit.root","tracksummary_kf.root",
           "trackstates_kf.root","performance_kf.root","measurements.root")
    frame=ROOT.RDataFrame("audit",str(args.output/"audit.root"))
    counts={name:int(frame.Sum["ULong64_t"](name).GetValue()) for name in (
        "generated","simhits","measurements","selected","fit_attempts","fit_tracks","invalid_covariance",
        "primary_measurements","original_proto_measurements","corrected_proto_measurements","primary_measurement_associations_raw")}
    counts["events"]=int(frame.Count().GetValue())
    if counts["events"]!=args.events or counts["generated"]!=args.events:
        raise RuntimeError("Candidate native output lost generated events")
    import numpy as np
    errors=json.loads((args.output/"error-table.json").read_text())
    data=ROOT.RDataFrame("measurements",str(args.output/"measurements.root")).AsNumpy(
        ["volume_id","var_loc0","var_loc1","clus_size_loc0","clus_size_loc1"])
    checked=0
    groups=(errors["groups"] if args.digitization=="gaussian" else
        [{"volume":e["volume"],**v} for e in errors["entries"] for v in e["value"]])
    for group in groups:
        mask=data["volume_id"]==group["volume"];index=group["index"]
        actual=data[f"var_loc{index}"][mask]
        if args.digitization=="geometric":
            sizes=data[f"clus_size_loc{index}"][mask]
            if np.any(sizes<=0):raise RuntimeError("Measured coordinate has empty cluster")
            rms=np.asarray(group["rms"])[np.minimum(sizes,len(group["rms"]))-1]
        else:rms=group["sigma_mm"]
        if not np.all(actual==np.asarray(rms*rms,dtype=actual.dtype)):
            raise RuntimeError("Native candidate measurement variance differs from remapped frozen errors")
        checked+=len(actual)
    if len(data["volume_id"])!=counts["measurements"]:
        raise RuntimeError("Native measurement ROOT and audit counts differ")
    return counts,{name:root_inventory(ROOT,args.output/name) for name in names},names,{"checked_marginals":checked,"exact_float32_variance_match":True}
