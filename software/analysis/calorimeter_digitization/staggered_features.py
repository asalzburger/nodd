"""Reconstructed-only ECAL features and physical-mask probes; full data stay local."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import numpy as np

from angular_sample import ROOT, save, sha
from untiled_geometry import location, number, polygon, rotation

FEATURE_NAMES = ["abs_reconstructed_eta", "exposure_5p5mm", "exposure_11mm",
                 "exposure_22mm", "missing_layer_streak_fraction", "near_sector_seam",
                 "early_energy_fraction", "late_energy_fraction", "other_section_fraction",
                 "lateral_width_over_22mm"]

NATIVE = r'''
#include <edm4hep/SimCalorimeterHitCollection.h>
#include <array>
#include <algorithm>
#include <vector>
#include <unordered_map>
#include <cmath>
#include <cstdint>
#include <stdexcept>
namespace nodd_staggering {
std::vector<double> cells(const edm4hep::SimCalorimeterHitCollection& hits) {
  // S, S*x/y/z, S*xx/yy/zz/xy/xz/yz, 48 layer sums, number of cells.
  std::vector<double> out(59, 0.);
  for (const auto& hit : hits) {
    const double e=hit.getEnergy(); const auto p=hit.getPosition();
    const int layer=(hit.getCellID()>>14)&63;
    if (!(std::isfinite(e)&&e>0&&std::isfinite(p.x)&&std::isfinite(p.y)&&std::isfinite(p.z)) || layer>=48)
      throw std::runtime_error("Invalid cell in feature extraction");
    out[0]+=e; out[1]+=e*p.x;out[2]+=e*p.y;out[3]+=e*p.z;
    out[4]+=e*p.x*p.x;out[5]+=e*p.y*p.y;out[6]+=e*p.z*p.z;
    out[7]+=e*p.x*p.y;out[8]+=e*p.x*p.z;out[9]+=e*p.y*p.z;
    out[10+layer]+=e;out[58]+=1.;
  }
  return out;
}
class Masks {
  struct Point {double x,y;};
  struct Poly {std::vector<Point> vertices;double xmin,xmax,ymin,ymax;};
  std::array<std::vector<Poly>,48> shapes[2];
  std::array<std::unordered_map<uint64_t,std::vector<int>>,48> buckets[2];
  double planes[2][48]{};
  static uint64_t key(int x,int y) {return (uint64_t(uint32_t(x))<<32)|uint32_t(y);}
  bool inside(int section,int layer,double x,double y) const {
    if(!std::isfinite(x)||!std::isfinite(y)||std::abs(x)>1e6||std::abs(y)>1e6)return false;
    const auto& index=buckets[section][layer];
    const auto found=index.find(key(int(std::floor(x/96.)),int(std::floor(y/96.))));
    if(found==index.end()) return false;
    for(int i:found->second) {
      const auto& p=shapes[section][layer][i];
      if(x<p.xmin-1e-7||x>p.xmax+1e-7||y<p.ymin-1e-7||y>p.ymax+1e-7) continue;
      bool good=true;
      for(size_t j=0;j<p.vertices.size();++j){auto a=p.vertices[j],b=p.vertices[(j+1)%p.vertices.size()];
        if((b.x-a.x)*(y-a.y)-(b.y-a.y)*(x-a.x)<-1e-7){good=false;break;}}
      if(good) return true;
    }
    return false;
  }
public:
  void plane(int section,int layer,double position){planes[section][layer]=position;}
  void add(int section,int layer,const std::vector<double>& x,const std::vector<double>& y){
    if(section<0||section>1||layer<0||layer>=48||x.size()!=y.size()||x.size()<3)
      throw std::runtime_error("Invalid mask");
    Poly p; p.xmin=p.xmax=x[0];p.ymin=p.ymax=y[0];
    for(size_t j=0;j<x.size();++j){p.vertices.push_back({x[j],y[j]});
      p.xmin=std::min(p.xmin,x[j]);p.xmax=std::max(p.xmax,x[j]);
      p.ymin=std::min(p.ymin,y[j]);p.ymax=std::max(p.ymax,y[j]);}
    const int i=shapes[section][layer].size();shapes[section][layer].push_back(p);
    for(int u=int(std::floor(p.xmin/96.));u<=int(std::floor(p.xmax/96.));++u)
      for(int v=int(std::floor(p.ymin/96.));v<=int(std::floor(p.ymax/96.));++v)
        buckets[section][layer][key(u,v)].push_back(i);
  }
  bool point(int section,int layer,double u,double v) const{return inside(section,layer,u,v);}
  std::vector<double> probe(double eta,double phi,double barrelFraction) const {
    const double pi=std::acos(-1.),period=pi/8.;
    double delta=std::fmod(phi+period/2.+4*pi,period)-period/2.;
    std::vector<double> out(4,0.); double norm=0.;
    for(int section=0;section<2;++section){
      std::array<double,3> sums{};double weights=0.;int longest=0,current=0;
      for(int layer=0;layer<48;++layer){
        const double z=planes[section][layer]; double u,v;
        if(section==0){u=z*std::tan(delta);v=z*std::sinh(eta)/std::cos(delta);}
        else {double sh=std::abs(std::sinh(eta));
          if(sh<1e-8){u=1e12;v=1e12;}else{u=z/sh*std::cos(delta);v=(eta>=0?1.:-1.)*z/sh*std::sin(delta);}}
        bool central=inside(section,layer,u,v);current=central?0:current+1;longest=std::max(longest,current);
        // Fixed analysis probe, not an asserted shower model: layer centre16,width8.
        const double weight=std::exp(-.5*std::pow((layer-16.)/8.,2));weights+=weight;
        const double kernels[3]={5.5,11.,22.};
        for(int k=0;k<3;++k){double value=0.,wn=0.;
          for(int dx=-2;dx<=2;++dx)for(int dy=-2;dy<=2;++dy){
            double w=std::exp(-.5*(dx*dx+dy*dy));wn+=w;
            if(inside(section,layer,u+dx*kernels[k],v+dy*kernels[k]))value+=w;}
          sums[k]+=weight*value/wn;
        }
      }
      double fraction=section==0?barrelFraction:1.-barrelFraction;
      for(int k=0;k<3;++k)out[k]+=fraction*sums[k]/weights;
      if((barrelFraction>=.5)==(section==0))out[3]=longest/48.;
      norm+=fraction;
    }
    return out;
  }
};
}
'''


def transform(node):
    return np.asarray(rotation(node)), np.asarray(location(node))


def vertices(piece):
    if piece.findall("cut"):
        raise ValueError("Unsupported sensitive mask with holes")
    if piece.get("kind") == "xtru":
        return polygon(piece)
    if piece.get("kind") == "box":
        u, v = number(piece.get("sx")) / 2, number(piece.get("sy")) / 2
        return [(-u, -v), (u, -v), (u, v), (-u, v)]
    raise ValueError("Unsupported sensitive primitive")


def masks_from_xml(compact):
    tree = ET.parse(compact)
    output = [[], []]
    for section, name in enumerate(("BARREL", "EDGE")):
        detector = tree.find(f"./detectors/detector[@name='{name}']")
        regions = {r.get("name"): r for r in detector.findall("region")}
        boards = {b.get("name"): b for b in detector.findall("board")}
        for layer in range(48):
            replicas = [r for r in detector.findall("replica")
                        if int(r.get("layer")) == layer and int(r.get("sector")) == 0
                        and int(r.get("side")) == (0 if section == 0 else 1)]
            shapes, plane = [], None
            for replica in replicas:
                region = regions[replica.get("region")]
                rr, rt = transform(replica)
                placements = []
                if section == 0:
                    for board in region.findall("board_instance"):
                        br, bt = transform(board)
                        for p in boards[board.get("template")].findall("piece"):
                            if p.get("role") == "sensitive":
                                placements.append((p, br, bt))
                else:
                    placements = [(p, np.eye(3), np.zeros(3)) for p in region.findall("piece")
                                  if p.get("role") == "sensitive"]
                for p, br, bt in placements:
                    pr, pt = transform(p)
                    points = np.array([[x, y, 0.] for x, y in vertices(p)])
                    points = (points @ pr.T + pt) @ br.T + bt
                    points = points @ rr.T + rt
                    normal = 0 if section == 0 else 2
                    position = float(points[:, normal].mean())
                    if np.ptp(points[:, normal]) > 1e-7:
                        raise ValueError("Sensitive mask is not coplanar")
                    if plane is not None and abs(position - plane) > 1e-7:
                        raise ValueError("Layer has inconsistent sensor depths")
                    plane = position
                    uv = points[:, [1, 2] if section == 0 else [0, 1]].tolist()
                    signed = sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(uv, uv[1:] + uv[:1]))
                    if signed < 0:
                        uv.reverse()
                    shapes.append(uv)
            if not shapes or plane is None:
                raise ValueError(f"Missing sensitive layer {name}:{layer}")
            output[section].append(dict(plane_mm=plane, polygons=shapes))
    return output


def extract(args):
    import ROOT as R
    import edm4hep
    from podio import root_io
    run, sample = args.run.resolve(), args.sample.resolve()
    proof = json.loads((run / "readback.json").read_text())
    receipt = json.loads((run / "receipt.json").read_text())
    if proof["status"] != "PASS" or receipt["exit_code"] or receipt["disk_abort"]:
        raise ValueError("Require successful transport and readback")
    if sha(run / "event-summary.jsonl") != proof["event_summary_sha256"] or sha(run / "receipt.json") != proof["receipt_sha256"]:
        raise ValueError("Changed audited source")
    if sha(sample / "sample.json") != receipt["sample_sha256"]:
        raise ValueError("Changed sample manifest")
    manifest = json.loads((sample / "sample.json").read_text())
    if sha(sample / "detector.xml") != manifest["hashes"]["detector.xml"]:
        raise ValueError("Changed compact")
    if sha(run / "events.root") != proof["root_sha256"]:
        raise ValueError("Changed ROOT file")
    rows = {r["event"]: r for r in (json.loads(line) for line in (run / "event-summary.jsonl").read_text().splitlines())}
    if set(rows) != set(range(10000)):
        raise ValueError("Require exact 10k primary IDs")
    geometry = masks_from_xml(sample / "detector.xml")
    R.gInterpreter.Declare(NATIVE)
    native = R.nodd_staggering.Masks()
    for section, layers in enumerate(geometry):
        for layer, entry in enumerate(layers):
            native.plane(section, layer, entry["plane_mm"])
            for p in entry["polygons"]:
                native.add(section, layer, R.std.vector("double")([v[0] for v in p]),
                           R.std.vector("double")([v[1] for v in p]))
    feature = np.zeros((10000, len(FEATURE_NAMES)))
    signal, response, true_energy, true_eta, true_phi = [np.zeros(10000) for _ in range(5)]
    region = np.zeros(10000, dtype=np.int64)
    valid = np.zeros(10000, dtype=bool)
    layer_signal = np.zeros((10000, 48))
    rec_eta, rec_phi = np.zeros(10000), np.zeros(10000)
    seen, cells = set(), 0
    for frame in root_io.Reader(str(run / "events.root")).get("events"):
        header, = frame.get("EventHeader")
        event = int(header.getEventNumber())
        if event in seen or event not in rows or int(header.getRunNumber()) != 0:
            raise ValueError("Invalid saved event identity")
        seen.add(event)
        barrel = np.asarray(list(R.nodd_staggering.cells(frame.get("BARRELHits"))))
        edge = np.asarray(list(R.nodd_staggering.cells(frame.get("EDGEHits"))))
        total = barrel + edge
        ref = rows[event]
        if not math.isclose(total[0], ref["signal_GeV"], rel_tol=1e-10, abs_tol=1e-12):
            raise ValueError("Feature sum differs from audited energy")
        cells += int(total[58])
        if int(total[58]) != sum(ref["counts"].values()):
            raise ValueError("Feature cell count differs")
        signal[event], response[event] = total[0], ref["response"]
        true_energy[event], true_eta[event], true_phi[event] = ref["energy_GeV"], ref["eta"], ref["phi"]
        layer_signal[event] = total[10:58]
        if total[0] > 0:
            centre = total[1:4] / total[0]
            radius = math.hypot(centre[0], centre[1])
            if radius > 1e-8 and np.linalg.norm(centre) > 1e-8:
                valid[event] = True
                eta, phi = math.asinh(centre[2] / radius), math.atan2(centre[1], centre[0])
                rec_eta[event], rec_phi[event] = eta, phi
                fraction = barrel[0] / total[0]
                region[event] = int(fraction < .5)
                exposure = list(native.probe(eta, phi, fraction))
                direction = centre / np.linalg.norm(centre)
                moment = np.array([[total[4], total[7], total[8]], [total[7], total[5], total[9]],
                                   [total[8], total[9], total[6]]]) / total[0]
                lateral = math.sqrt(max(0., np.trace(moment) - direction @ moment @ direction))
                period = math.pi / 8
                delta = (phi + period / 2) % period - period / 2
                seam_distance = radius * math.sin(period / 2 - abs(delta))
                feature[event] = [abs(eta), *exposure,
                    math.exp(-.5 * (seam_distance / 22) ** 2),
                    total[10:26].sum() / total[0], total[42:58].sum() / total[0],
                    min(fraction, 1 - fraction), lateral / 22]
        if len(seen) % 1000 == 0:
            print(f"Reconstructed and mask-probed {len(seen)}/10000 events", flush=True)
    if seen != set(rows) or not np.all(np.isfinite(feature)):
        raise ValueError("Incomplete/nonfinite reconstructed features")
    args.output.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(args.output / "features.npz", features=feature, signal=signal, response=response,
        energy=true_energy, eta=true_eta, phi=true_phi, region=region, valid_axis=valid,
        reconstructed_eta=rec_eta, reconstructed_phi=rec_phi, layer_signal=layer_signal,
        event=np.arange(10000, dtype=np.int64))
    save(args.output / "masks.json", geometry)
    save(args.output / "receipt.json", dict(status="PASS", events=10000, cell_hits=cells,
        valid_axes=int(valid.sum()), zero_signals=int(np.count_nonzero(signal == 0)),
        feature_names=FEATURE_NAMES, inference_inputs="Persisted cell energies/positions/IDs and fixed physical masks only; no truth energy/direction",
        mask_probe="Gaussian transverse widths5.5/11/22mm,5x5 samples; fixed longitudinal Gaussian centre16,width8layers; analysis probes only",
        feature_sha256=sha(args.output / "features.npz"), masks_sha256=sha(args.output / "masks.json"),
        producer_sha256=sha(__file__), geometry_helper_sha256=sha(Path(__file__).with_name("untiled_geometry.py")),
        source_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        readback_sha256=sha(run / "readback.json"), root_sha256=proof["root_sha256"],
        sample_sha256=sha(sample / "sample.json"), compact_sha256=sha(sample / "detector.xml")))
    print(f"Saved reconstructed-only features: {valid.sum()} valid axes, {cells} cells", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    extract(parser.parse_args())
