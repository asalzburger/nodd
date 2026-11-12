"""Dense physical active-mask ray screening, not simulated efficiency/resolution."""
import argparse
import json
from pathlib import Path
import numpy as np

from angular_sample import save, sha
from staggered_features import NATIVE, masks_from_xml

SCREEN = r'''
namespace nodd_staggering {
std::vector<unsigned short> screen(const Masks& masks,const std::vector<double>& etas,
 const std::vector<double>& phis,const std::vector<double>& barrel,const std::vector<double>& edge){
 std::vector<unsigned short> output;output.reserve(etas.size()*phis.size()*4);
 for(double eta:etas)for(double phi:phis){int count[2]={0,0},longest[2]={0,0};
  for(int section=0;section<2;++section){int streak=0;
   for(int layer=0;layer<48;++layer){double u,v;
    if(section==0){u=barrel[layer]*std::tan(phi);v=barrel[layer]*std::sinh(eta)/std::cos(phi);}
    else{double sh=std::abs(std::sinh(eta));if(sh<1e-8){u=v=1e12;}
     else{u=edge[layer]/sh*std::cos(phi);v=(eta>=0?1.:-1.)*edge[layer]/sh*std::sin(phi);}}
    bool active=masks.point(section,layer,u,v);count[section]+=active;
    streak=active?0:streak+1;longest[section]=std::max(longest[section],streak);
   }
  }
  output.push_back(count[0]);output.push_back(count[1]);
  output.push_back(longest[0]);output.push_back(longest[1]);
 }
 return output;
}
}
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--staggered',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    import ROOT as R
    R.gInterpreter.Declare(NATIVE+SCREEN)
    eta=np.linspace(-3,3,3001);phi=(np.arange(360)+.5)/360*np.pi/8-np.pi/16
    a.output.mkdir(parents=True,exist_ok=False)
    summary=dict(status='PROTOTYPE geometric screening only',eta_range=[-3,3],eta_points=len(eta),
        signed_fold_phi_degrees=[-11.25,11.25],phi_points=len(phi),rays_per_geometry=len(eta)*len(phi),
        definition='Exact polygon plane intersections, barrel+endcap sum can exceed48 near transition; not shower efficiency',
        producer_sha256=sha(__file__),geometries={})
    for label,compact in (('baseline',a.baseline),('staggered',a.staggered)):
        geometry=masks_from_xml(compact);native=R.nodd_staggering.Masks()
        for section,layers in enumerate(geometry):
            for layer,entry in enumerate(layers):
                native.plane(section,layer,entry['plane_mm'])
                for poly in entry['polygons']:
                    native.add(section,layer,R.std.vector('double')([p[0] for p in poly]),R.std.vector('double')([p[1] for p in poly]))
        counts=np.array(list(R.nodd_staggering.screen(native,R.std.vector('double')(eta.tolist()),
            R.std.vector('double')(phi.tolist()),R.std.vector('double')([e['plane_mm'] for e in geometry[0]]),
            R.std.vector('double')([e['plane_mm'] for e in geometry[1]]))),dtype=np.int16).reshape(len(eta),len(phi),4)
        total=counts[:,:,:2].sum(axis=2)
        dominant=np.where(counts[:,:,0]>=counts[:,:,1],counts[:,:,2],counts[:,:,3])
        np.savez_compressed(a.output/f'{label}-rays.npz',eta=eta,phi=phi,counts=counts)
        summary['geometries'][label]=dict(compact_sha256=sha(compact),minimum_plane_intersections=int(total.min()),
            maximum_plane_intersections=int(total.max()),mean_plane_intersections=float(total.mean()),
            zero_intersection_rays=int((total==0).sum()),zero_intersection_fraction=float((total==0).mean()),
            plane_intersection_histogram=np.bincount(total.ravel(),minlength=97).tolist(),
            dominant_section_missing_streak_histogram=np.bincount(dominant.ravel(),minlength=49).tolist(),
            per_abs_eta_halfunit=[dict(low=float(lo),high=float(lo+.5),rays=int(m.sum()*len(phi)),
                mean_intersections=float(total[m].mean()),zero_fraction=float((total[m]==0).mean()))
                for lo in np.arange(0,3,.5) for m in [(abs(eta)>=lo)&(abs(eta)<lo+.5 if lo<2.5 else abs(eta)<=3)]])
        print(label,summary['geometries'][label]['mean_plane_intersections'],summary['geometries'][label]['zero_intersection_fraction'],flush=True)
    save(a.output/'screen.json',summary)


if __name__=='__main__':main()
