#!/usr/bin/env python3
"""Native straight-ray characterization of the DES025 tracker prototype.

ROOT boundary navigation integrates every material volume, including passive
services. No ACTS thin-surface material approximation or reconstruction is used.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
CATEGORIES = ["Beam pipe", "Pixel", "Short-strip barrel", "Short-strip endcap",
              "Long-strip barrel", "Long-strip endcap", "Shared short-strip services"]
COMPONENT_CATEGORY = dict(zip(["beam", "pixel", "short_barrel", "short_endcap",
                              "long_barrel", "long_endcap", "shared_short_services"], CATEGORIES))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def direction(eta, phi):
    return [math.cos(phi) / math.cosh(eta), math.sin(phi) / math.cosh(eta), math.tanh(eta)]


def station(ids):
    return f"{ids['system']}:{ids['layer']}"


def hit_metrics(sensors, ideal):
    """Separate patches, physical sensors, and same-module paired stations."""
    physical, reached, pairs = set(), set(), defaultdict(set)
    for item in sensors:
        ids = item["ids"]
        key = tuple(sorted((k, v) for k, v in ids.items() if k != "sensor"))
        if ids["system"] <= 3:  # multiple chip islands share one sensor substrate
            physical.add(key)
            reached.add(station(ids))
        elif ids["system"] <= 5:
            physical.add(tuple(sorted(ids.items())))
            reached.add(station(ids))
        else:
            physical.add(tuple(sorted(ids.items())))
            pairs[key].add(ids["sensor"])
    complete = sum(faces == {0, 1} for faces in pairs.values())
    for key, faces in pairs.items():
        if faces == {0, 1}:
            reached.add(station(dict(key)))
    return dict(active_patches=len(sensors), physical_sensors=len(physical),
                complete_long_strip_pairs=complete,
                orphan_long_strip_faces=sum(len(f) for f in pairs.values()) - 2 * complete,
                stations=len(reached), ideal_stations=len(ideal),
                holes=len(set(ideal) - reached), extra_stations=len(reached - set(ideal)),
                missing_station_ids=sorted(set(ideal) - reached))


def ideal_reference():
    """Present disc datums with the frozen declared ideal active radial bounds."""
    frozen = ROOT_DIR / "docs/validation/DES-013-pixel-z/data/packed-200um/layout.json.gz"
    layers = json.loads(gzip.decompress(frozen.read_bytes()))["layers"]
    result = []
    for item in layers:
        if item["subsystem"] != "pixel" or item["kind"] != "cylinder":
            continue
        result.append(dict(id=f"1:{int(item['id'].split('B')[-1])}", kind="cylinder",
                           radius_mm=item["r_m"] * 1000,
                           z_min_mm=item["z_min_m"] * 1000, z_max_mm=item["z_max_m"] * 1000))
    pixel = json.loads((ROOT_DIR / "tools/pixel_endcap_support/inputs.json").read_text())
    radial = json.loads((ROOT_DIR / "tools/pixel_disc_optimization/radial-inputs.json").read_text())
    # The source explicitly distinguishes the active target from passive plate/service bounds.
    annulus = radial["annulus_mm"]
    for system, sign in ((2, -1), (3, 1)):
        for index, z in enumerate(pixel["placement"]["disc_abs_z_mm"], 1):
            result.append(dict(id=f"{system}:{index}", kind="disc", z_mm=sign * z,
                               r_min_mm=annulus[0], r_max_mm=annulus[1]))
    for system, path in ((4, "tools/short_strip_barrel/inputs-phi-tilted.json"),
                         (6, "tools/long_strip_barrel/inputs.json")):
        cfg = json.loads((ROOT_DIR / path).read_text())
        for index, radius in enumerate(cfg.get("nominal_radii_mm", cfg.get("radii_mm"))):
            result.append(dict(id=f"{system}:{index}", kind="cylinder", radius_mm=radius,
                               z_min_mm=-cfg["active_half_length_mm"], z_max_mm=cfg["active_half_length_mm"]))
    for system, path in ((5, "tools/short_strip_endcap/inputs.json"),
                         (7, "tools/long_strip_endcap/inputs.json")):
        cfg = json.loads((ROOT_DIR / path).read_text())
        for sign, offset in ((1, 0), (-1, len(cfg["disc_z_mm"]))):
            for index, z in enumerate(cfg["disc_z_mm"]):
                result.append(dict(id=f"{system}:{index + offset}", kind="disc", z_mm=sign * z,
                                   r_min_mm=cfg["annulus_mm"][0], r_max_mm=cfg["annulus_mm"][1]))
    return result


def ideal_crossings(layers, origin, ray, tolerance_mm=1e-6):
    result = set()
    for layer in layers:
        if layer["kind"] == "cylinder":
            a = ray[0] ** 2 + ray[1] ** 2
            b = origin[0] * ray[0] + origin[1] * ray[1]
            c = origin[0] ** 2 + origin[1] ** 2 - layer["radius_mm"] ** 2
            disc = b * b - a * c
            if disc < 0 or a == 0:
                continue
            t = (-b + math.sqrt(disc)) / a
            z = origin[2] + t * ray[2]
            inside = layer["z_min_mm"] - tolerance_mm <= z <= layer["z_max_mm"] + tolerance_mm
        else:
            if abs(ray[2]) < 1e-15:
                continue
            t = (layer["z_mm"] - origin[2]) / ray[2]
            r = math.hypot(origin[0] + t * ray[0], origin[1] + t * ray[1])
            inside = layer["r_min_mm"] - tolerance_mm <= r <= layer["r_max_mm"] + tolerance_mm
        if t > tolerance_mm and inside:
            result.add(layer["id"])
    return result


CPP = r'''
#include <TGeoManager.h>
#include <TGeoNavigator.h>
#include <TGeoMatrix.h>
#include <TGeoBBox.h>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cmath>
#include <stdexcept>
namespace issue38 {
std::map<std::string,int> categories, sensitive;
struct Sensor {int index; std::vector<double> center, u, v, size;};
std::vector<Sensor> native;
void visit(TGeoNode* node, const TGeoHMatrix& parent) {
  TGeoHMatrix matrix(parent); matrix.Multiply(node->GetMatrix());
  auto vol=node->GetVolume(); auto found=sensitive.find(vol->GetName());
  if(found!=sensitive.end()) {
    double p[3]={0,0,0},q[3]; matrix.LocalToMaster(p,q);
    auto rot=matrix.GetRotationMatrix(); auto box=dynamic_cast<TGeoBBox*>(vol->GetShape());
    if(!box) throw std::runtime_error("non-box sensitive shape");
    native.push_back({found->second,{q[0],q[1],q[2]},
      {rot[0],rot[3],rot[6]},{rot[1],rot[4],rot[7]},
      {2*box->GetDX(),2*box->GetDY(),2*box->GetDZ()}});
  }
  for(int i=0;i<vol->GetNdaughters();++i) visit(vol->GetNode(i),matrix);
}
struct Ray {std::vector<int> hits; std::vector<double> x0, interaction;
  std::map<std::string,double> paths;
  double totalX0=0,totalInteraction=0,distance=0; int steps=0;};
Ray trace(TGeoManager* manager, std::vector<double> origin, std::vector<double> dir,
          double unit, double maxLength) {
  manager->InitTrack(origin[0]*unit,origin[1]*unit,origin[2]*unit,dir[0],dir[1],dir[2]);
  auto nav=manager->GetCurrentNavigator(); Ray out; std::set<int> hits;
  out.x0.resize(7);out.interaction.resize(7);
  while(!nav->IsOutside() && out.distance<maxLength) {
    auto node=nav->GetCurrentNode(); if(!node) break;
    auto vol=node->GetVolume(); std::string name=vol->GetName();
    auto mat=vol->GetMaterial();
    bool world=vol==manager->GetTopVolume();
    nav->FindNextBoundaryAndStep((maxLength-out.distance)*unit);
    double step=nav->GetStep()/unit;
    if(!std::isfinite(step) || step<=0) throw std::runtime_error("invalid/zero native boundary step at "+name);
    out.distance+=step;
    auto s=sensitive.find(name);if(s!=sensitive.end())hits.insert(s->second);
    if(!world) {
      int cat=-1;auto c=categories.find(name);if(c!=categories.end())cat=c->second;
      if(std::string(mat->GetName())=="Beryllium" || std::string(mat->GetName())=="Vacuum")cat=0;
      if(cat<0) throw std::runtime_error("unclassified native material volume "+name);
      if(mat->GetRadLen()<=0 || mat->GetIntLen()<=0)
        throw std::runtime_error("invalid material length at "+name);
      double x=mat->GetRadLen()>0?step*unit/mat->GetRadLen():0;
      double l=mat->GetIntLen()>0?step*unit/mat->GetIntLen():0;
      out.x0[cat]+=x;out.interaction[cat]+=l;
      out.totalX0+=x;out.totalInteraction+=l;out.paths[mat->GetName()]+=step;
    }
    if(++out.steps>100000)throw std::runtime_error("native boundary step limit");
  }
  out.hits.assign(hits.begin(),hits.end());return out;
}
}
'''


def plot(report, output):
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = report["rays"]
    eta, phi, origins = report["sampling"]["eta"], report["sampling"]["phi"], report["sampling"]["origins_mm"]
    shape = (len(origins), len(eta), len(phi))
    fig, axes = plt.subplots(3, 2, figsize=(13, 12), constrained_layout=True)
    for column, metric in enumerate(("physical_sensors", "holes")):
        data = np.array([r[metric] for r in rows]).reshape(shape)
        avg = data.mean(axis=0)
        image = axes[0, column].pcolormesh(phi, eta, avg, shading="nearest", cmap="viridis" if column == 0 else "magma")
        axes[0, column].set(xlabel=r"$\phi$ [rad]", ylabel=r"$\eta$", title="Mean physical active sensors" if column == 0 else "Mean missed ideal stations (holes)")
        fig.colorbar(image, ax=axes[0, column], label="count; mean over three z vertices")
        image = axes[1, column].pcolormesh(phi, eta, data[1], shading="nearest", cmap="viridis" if column == 0 else "magma")
        axes[1, column].set(xlabel=r"$\phi$ [rad]", ylabel=r"$\eta$", title="Physical active sensors, z = 0" if column == 0 else "Missed ideal stations, z = 0")
        fig.colorbar(image, ax=axes[1, column], label="count at z = 0 mm")
    for metric, style in (("active_patches", ":"), ("physical_sensors", "-"),
                          ("stations", "-"), ("ideal_stations", "--"), ("holes", "-")):
        data = np.array([r[metric] for r in rows]).reshape(shape)
        axes[2, 0].plot(eta, data.mean(axis=(0, 2)), style, label=metric.replace("_", " "))
        axes[2, 1].plot(phi, data.mean(axis=(0, 1)), style, label=metric.replace("_", " "))
    for ax, xlab in zip(axes[2], (r"$\eta$", r"$\phi$ [rad]")):
        ax.set(xlabel=xlab, ylabel="mean count"); ax.legend(); ax.grid(alpha=.25)
    fig.suptitle("DES025 tracker prototype — native DD4hep/ROOT straight rays, B = 0\n"
                 "z = −150, 0, +150 mm; present disc datums / declared ideal active bounds", fontsize=13)
    fig.savefig(output / "coverage.png", dpi=160); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.8), constrained_layout=True)
    for ax, field, label in zip(axes, ("x0_by_component", "interaction_by_component"), (r"$X/X_0$", r"$L/\lambda_I$")):
        values = np.array([r[field] for r in rows]).reshape((*shape, len(CATEGORIES))).mean(axis=(0, 2))
        ax.stackplot(eta, values.T, labels=CATEGORIES)
        ax.set(xlabel=r"$\eta$", ylabel=label); ax.grid(alpha=.2)
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncols=4, fontsize=8)
    fig.suptitle("Full material represented in DES025 tracker + beam pipe\n"
                 "Native volume-boundary integration; mean over φ and z; world air excluded", fontsize=13)
    fig.savefig(output / "material.png", dpi=160); plt.close(fig)


def summarize(rows):
    fields = ["active_patches", "physical_sensors", "complete_long_strip_pairs",
              "orphan_long_strip_faces", "stations", "ideal_stations", "holes",
              "extra_stations", "x_over_x0", "l_over_lambda"]
    return dict(count=len(rows), fraction_without_sampled_hole=sum(r["holes"] == 0 for r in rows) / len(rows),
                quantities={k: dict(min=min(r[k] for r in rows), mean=statistics.mean(r[k] for r in rows),
                                    max=max(r[k] for r in rows)) for k in fields})


def load_report(output):
    report = json.loads((output / "summary.json").read_text())
    archive = output / report["ray_artifact"]["filename"]
    if sha(archive) != report["ray_artifact"]["sha256"]:
        raise ValueError("Retained ray artifact hash mismatch")
    report.update(json.loads(gzip.decompress(archive.read_bytes())))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact", type=Path)
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--library-dir", type=Path)
    parser.add_argument("--factory-source", type=Path, help="Source checkout associated with the reused factory build")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--eta-bins", type=int, default=41)
    parser.add_argument("--phi-bins", type=int, default=64)
    parser.add_argument("--plot-only", action="store_true")
    args = parser.parse_args()
    if args.plot_only:
        plot(load_report(args.output), args.output)
        return
    if not all((args.compact, args.expected, args.library_dir)):
        parser.error("--compact, --expected, --library-dir required for native scans")
    if (args.output / "summary.json").exists() or (args.output / "rays.json.gz").exists():
        parser.error("Use a fresh output directory; existing evidence is retained")
    if args.eta_bins < 2 or args.phi_bins < 1:
        parser.error("eta-bins >= 2 and phi-bins >= 1 required")
    import ROOT as R
    import dd4hep
    R.gROOT.SetBatch(True)
    expected = json.loads(args.expected.read_text())
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    libs = [args.library_dir / f"lib{name}{suffix}" for name in
            ("nODDBeamPipe", "nODDPixelBarrel", "nODDShortStripBarrel", "nODDShortStripEndcap", "nODDLongStrip")]
    source_files = sorted([*ROOT_DIR.glob("detector/src/*.cpp"), *ROOT_DIR.glob("detector/include/**/*.hpp"),
                           *ROOT_DIR.glob("prototypes/short_strip_*/*.cpp"),
                           ROOT_DIR / "prototypes/long_strip_barrel/LongStrip.cpp"])
    factory_identity = None
    if args.factory_source:
        for path in source_files:
            if sha(path) != sha(args.factory_source / path.relative_to(ROOT_DIR)):
                raise RuntimeError("Reused factory source differs: " + str(path))
        factory_identity = dict(source_revision=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=args.factory_source, text=True).strip(),
            source_status=subprocess.check_output(["git", "status", "--short"], cwd=args.factory_source, text=True),
            source_sha256={str(p.relative_to(ROOT_DIR)): sha(p) for p in source_files},
            note="Associated source bytes match; reused compiled artifacts separately hashed, no rebuild performed")
    for lib in libs:
        if R.gSystem.Load(str(lib.resolve())) < 0:
            raise RuntimeError("Factory load failed: " + str(lib))
    R.gInterpreter.Declare(CPP)
    sensors = [e for e in expected["entities"] if e["role"] == "sensitive"]
    for entity in expected["entities"]:
        R.issue38.categories[entity["name"]] = CATEGORIES.index(COMPONENT_CATEGORY[entity["component"]])
    for index, entity in enumerate(sensors):
        R.issue38.sensitive[entity["name"]] = index
    detector = dd4hep.Detector.getInstance()
    detector.fromXML(str(args.compact.resolve()))
    manager, unit = detector.manager(), float(dd4hep.mm)
    R.issue38.visit(manager.GetTopNode(), R.TGeoHMatrix())
    if len(R.issue38.native) != len(sensors):
        raise RuntimeError("Native sensitive count differs from exported inventory")
    max_center = max_axes = max_size = 0.0
    seen = set()
    for actual in R.issue38.native:
        index = int(actual.index)
        if index in seen:
            raise RuntimeError("Duplicate native sensitive placement")
        seen.add(index); wanted = sensors[index]
        max_center = max(max_center, math.dist([x / unit for x in actual.center], wanted["center_mm"]))
        max_size = max(max_size, math.dist([x / unit for x in actual.size], wanted["size_mm"]))
        for key in ("u", "v"):
            if key in wanted:
                max_axes = max(max_axes, math.dist(list(getattr(actual, key)), wanted[key]))
    if max_center > 1e-7 or max_size > 1e-7 or max_axes > 1e-9:
        raise RuntimeError(f"Native geometry differs: {max_center}, {max_axes}, {max_size}")
    print(f"Matched {len(sensors)} native sensitive patches; scanning...", flush=True)
    eta = [-4 + 8 * i / (args.eta_bins - 1) for i in range(args.eta_bins)]
    phi = [2 * math.pi * (i + .371) / args.phi_bins for i in range(args.phi_bins)]
    origins = [[0., 0., z] for z in (-150., 0., 150.)]
    layers, rays = ideal_reference(), []
    beam_config = expected["beam"]["config"]
    stop_radius = expected["config"]["tracker_region_rmax_mm"]
    stop_half_z = max(expected["config"]["tracker_region_zmax_mm"], beam_config["world_half_size_mm"][2])
    properties = {str(m.GetName()): dict(radiation_length_mm=float(m.GetRadLen()) / unit,
                                       interaction_length_mm=float(m.GetIntLen()) / unit)
                  for m in manager.GetListOfMaterials()}
    closure = pipe_residual = path_closure = 0.0
    controls = []
    samples = [(o, e, p, False) for o in origins for e in eta for p in phi]
    samples += [([0., 0., 0.], float(e), p + math.pi / args.phi_bins, True)
                for e in range(-4, 5) for p in phi]
    for origin, e, p, control in samples:
        ray = direction(e, p)
        # Exit the entire tracker service envelope; retain the full finite pipe.
        transverse = stop_radius / math.hypot(ray[0], ray[1])
        axial = ((stop_half_z if ray[2] > 0 else -stop_half_z) - origin[2]) / ray[2] if ray[2] else math.inf
        native = R.issue38.trace(manager, origin, ray, unit, min(transverse, axial))
        materials = {str(x.first): float(x.second) for x in native.paths}
        expected_pipe = beam_config["wall_mm"] * math.cosh(e)
        residual = abs(materials.get("Beryllium", 0.) - expected_pipe)
        pipe_residual = max(pipe_residual, residual)
        x0, interaction = list(native.x0), list(native.interaction)
        closure = max(closure, abs(sum(x0) - native.totalX0), abs(sum(interaction) - native.totalInteraction))
        for prop, total in (("radiation_length_mm", native.totalX0), ("interaction_length_mm", native.totalInteraction)):
            reconstructed = sum(length / properties[name][prop] for name, length in materials.items() if properties[name][prop] > 0)
            path_closure = max(path_closure, abs(reconstructed - total))
        metrics = hit_metrics([sensors[int(i)] for i in native.hits], ideal_crossings(layers, origin, ray))
        (controls if control else rays).append(dict(eta=e, phi=p, origin_mm=origin, **metrics,
                         x0_by_component=x0, interaction_by_component=interaction,
                         x_over_x0=float(native.totalX0), l_over_lambda=float(native.totalInteraction),
                         material_path_mm=materials, distance_mm=float(native.distance), boundary_steps=int(native.steps)))
        if len(rays) % args.phi_bins == 0 and not control:
            print(f"z={origin[2]:g} eta={e:g}", flush=True)
    if pipe_residual > 1e-6 or max(closure, path_closure) > 1e-12:
        raise RuntimeError(f"Material checks failed: pipe={pipe_residual}mm closure={closure} path={path_closure}")
    files = [args.compact, args.expected, args.compact.parent / "materials.xml", Path(__file__), *libs]
    refs = ["docs/validation/DES-013-pixel-z/data/packed-200um/layout.json.gz",
            "tools/pixel_disc_optimization/radial-inputs.json", "tools/pixel_endcap_support/inputs.json",
            "tools/short_strip_barrel/inputs-phi-tilted.json", "tools/short_strip_endcap/inputs.json",
            "tools/long_strip_barrel/inputs.json", "tools/long_strip_endcap/inputs.json"]
    report = dict(status="CHARACTERIZATION", scientific_acceptance="not assessed", material_properties=properties,
                  categories=CATEGORIES, ideal_reference=layers,
                  sampling=dict(eta=eta, phi=phi, origins_mm=origins, field_T=0,
                                seed=None, measure="deterministic uniform eta/phi grid, equal vertex weights",
                                phi_bin_phase=.371, stop_radius_mm=stop_radius,
                                stop_abs_z_mm=stop_half_z, ideal_bound_tolerance_mm=1e-6,
                                offset_phi_control="half phi-bin shift, x=y=z=0, eta=-4,-3,...,4; kept separate from means"),
                  checks=dict(native_sensitive_patches=len(sensors), maximum_center_residual_mm=max_center,
                              maximum_axis_residual=max_axes, maximum_size_residual_mm=max_size,
                              maximum_pipe_path_residual_mm=pipe_residual, maximum_stack_closure=closure,
                              maximum_material_path_reintegration_residual=path_closure,
                              native_zero_step_count=0),
                  execution=dict(source_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT_DIR, text=True).strip(),
                                 source_worktree_status=subprocess.check_output(["git", "status", "--short"], cwd=ROOT_DIR, text=True),
                                 command=sys.argv, python=sys.version, root_version=R.gROOT.GetVersion(),
                                 platform=platform.platform(), hashes={str(p.resolve()): sha(p) for p in files},
                                 reference_sha256={p: sha(ROOT_DIR / p) for p in refs},
                                 reused_factory_source=factory_identity,
                                 environment_fingerprints={str(p): sha(p) for p in [
                                     Path("/Users/salzburg/cernbox/configs/acts/acts_setup.sh"),
                                     Path("/Users/salzburg/Documents/work/externals/ci-dependencies/spack.lock")]
                                     if p.exists()}),
                  limitations=["Geometric straight-ray crossings, not reconstructed hits, tracking efficiency, or a magnetic-field study.",
                               "All native material in this tracker+pipe prototype is included; omitted detector hardware is not restored by the scan.",
                               "World air excluded; air/vacuum explicitly enclosed by components included. Effective-material recipes retained.",
                               "Holes use declared active ideal bounds with current disc datums, distinct from frozen original coverage denominators.",
                               "Finite sampling at x=y=0 and three z vertices does not prove continuous luminous-volume hermeticity.",
                               "No digitization, dead channels, alignment, scattering, energy loss, reconstruction, or engineering sign-off."])
    args.output.mkdir(parents=True, exist_ok=True)
    archive = args.output / "rays.json.gz"
    archive.write_bytes(gzip.compress(json.dumps(dict(rays=rays, offset_phi_controls=controls), separators=(",", ":")).encode(), mtime=0))
    report["ray_artifact"] = dict(filename=archive.name, sha256=sha(archive), main_count=len(rays), offset_phi_control_count=len(controls))
    report["aggregates"] = dict(main=summarize(rays), offset_phi_controls=summarize(controls),
                                by_vertex=[dict(origin_mm=o, **summarize([r for r in rays if r["origin_mm"] == o])) for o in origins],
                                by_eta=[dict(eta=e, **summarize([r for r in rays if r["eta"] == e])) for e in eta],
                                by_phi=[dict(phi=p, **summarize([r for r in rays if r["phi"] == p])) for p in phi],
                                offset_controls_by_eta=[dict(eta=e, **summarize([r for r in controls if r["eta"] == e])) for e in range(-4, 5)])
    (args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    plot(dict(report, rays=rays, offset_phi_controls=controls), args.output)
    print(json.dumps(dict(rays=len(rays), checks=report["checks"], max_holes=max(r["holes"] for r in rays))))
    dd4hep.Detector.destroyInstance()
    if R.gGeoManager:
        R.gGeoManager.Delete()


if __name__ == "__main__":
    main()
