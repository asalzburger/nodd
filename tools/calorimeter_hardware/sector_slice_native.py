"""Render XY material/sensitivity slices by navigating the actual DD4hep geometry.

Run in software/env/run.sh. No event transport or idealized replacement solids.
"""
import argparse, hashlib, json, math, struct, subprocess, zlib
from pathlib import Path

CPP = r'''
#include <TGeoManager.h>
#include <TGeoNavigator.h>
#include <TGeoVolume.h>
#include <vector>
#include <cmath>
#include <stdexcept>
namespace NativeXY {
std::vector<unsigned char> render(TGeoManager* g, double mm,
 const std::vector<double>& pal, double x0,double x1,double y0,double y1,
 double z,int nx,int ny,int sub,bool angular) {
 std::vector<double> rgb(nx*ny*3,0.);
 for(int iy=0;iy<ny;++iy) for(int sy=0;sy<sub;++sy) {
  double y=y1-(iy+(sy+.5)/sub)*(y1-y0)/ny;
  g->InitTrack(x0*mm,y*mm,z*mm,1.,0.,0.);
  auto n=g->GetCurrentNavigator(); double distance=0.;int count=0;
  while(!n->IsOutside() && distance<x1-x0-1.e-8) {
   auto node=n->GetCurrentNode();if(!node)break;
   int id=node->GetVolume()->GetNumber();
   n->FindNextBoundaryAndStep((x1-x0-distance)*mm);
   double step=n->GetStep()/mm;
   if(!std::isfinite(step)||step<0)throw std::runtime_error("Invalid native step");
   if(step<1.e-9)throw std::runtime_error("Zero native step");
   double a=distance*nx/(x1-x0),b=std::min(double(nx),(distance+step)*nx/(x1-x0));
   for(int ix=std::max(0,int(std::floor(a)));ix<std::min(nx,int(std::ceil(b)));++ix) {
    double w=std::max(0.,std::min(b,ix+1.)-std::max(a,double(ix)))/sub;
    bool mask=angular&&std::abs(std::atan2(x0+(ix+.5)*(x1-x0)/nx,y))>M_PI/8.;
    for(int k=0;k<3;++k)rgb[(iy*nx+ix)*3+k]+=w*(mask?255.:pal[id*3+k]);
   }
   distance+=step;if(++count>100000)throw std::runtime_error("Native step guard");
  }
 }
 std::vector<unsigned char> out(rgb.size());for(size_t i=0;i<out.size();++i)out[i]=std::round(std::max(0.,std::min(255.,rgb[i])));return out;
}
std::vector<double> ray(TGeoManager* g,double mm,const std::vector<int>& sensitive,
 double angle,double z,double rmax) {
 g->InitTrack(0.,0.,z*mm,std::cos(angle),std::sin(angle),0.);
 auto n=g->GetCurrentNavigator();double distance=0.;int count=0;std::vector<double> out;
 while(!n->IsOutside()&&distance<rmax-1.e-8) {
  auto node=n->GetCurrentNode();if(!node)break;int id=node->GetVolume()->GetNumber();
  n->FindNextBoundaryAndStep((rmax-distance)*mm);double step=n->GetStep()/mm;
  if(!std::isfinite(step)||step<=0)throw std::runtime_error("Invalid ray step");
  if(sensitive[id]){out.push_back(distance);out.push_back(step);out.push_back(id);}
  distance+=step;if(++count>100000)throw std::runtime_error("Ray guard");
 }return out;
}
}
'''

def png(path, nx, ny, data):
    def chunk(tag,payload):return struct.pack('!I',len(payload))+tag+payload+struct.pack('!I',zlib.crc32(tag+payload)&0xffffffff)
    raw=b''.join(b'\0'+data[y*nx*3:(y+1)*nx*3] for y in range(ny))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',nx,ny,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))

def drawing_geometry(expected):
    """Declared model dimensions for labels; native solids remain the image source."""
    if 'config' in expected and 'sampling_inner_radius_mm' in expected['config']:
        c=expected['config']
        return dict(kind='inclined_lar',sampling_inner_radius_mm=c['sampling_inner_radius_mm'],
            sampling_outer_radius_mm=c['sampling_outer_radius_mm'],warm_inner_radius_mm=c['warm_inner_radius_mm'],
            warm_outer_radius_mm=expected['envelopes']['outer_radius_mm'],planes=c['planes'],
            lead_mm=c['lead_mm'],electrode_mm=c['electrode_mm'],inclination_deg=c['inclination_deg'])
    r=expected['layout_report'];e=r['envelopes']
    return dict(kind='siw_sector',stack_front_apothem_mm=e['ecal_barrel_front_mm'],
        stack_outer_apothem_mm=e['ecal_barrel_outer_mm'],layers=r['assembly_config']['ecal_layers'],
        layer_pitch_mm=r['layer_pitch_mm'],tungsten_mm=r['ecal']['absorber_mm'],silicon_mm=r['ecal']['sensor_mm'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--compact',type=Path,required=True);p.add_argument('--library',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--z',type=float,default=0.)
    p.add_argument('--zoom-bounds',type=float,nargs=4,metavar=('X0','X1','Y0','Y1'))
    p.add_argument('--geometry-revision',help='Also require every geometry input to match this full repository commit')
    p.add_argument('--library-sha256',help='Require the exact previously validated factory library bytes')
    a=p.parse_args()
    expected_file=a.compact.parent/'expected.json';expected=json.loads(expected_file.read_text());repo=Path(__file__).resolve().parents[2]
    revision=expected['execution']['commit']
    resolved=subprocess.check_output(['git','rev-parse','--verify',revision+'^{commit}'],cwd=repo,text=True).strip()
    if revision!=resolved:raise ValueError('Model source must identify a full commit SHA')
    for name,want in expected['source_sha256'].items():
        source=subprocess.check_output(['git','show',revision+':'+name],cwd=repo)
        if hashlib.sha256(source).hexdigest()!=want:raise ValueError('Model input differs from declared source commit: '+name)
        if a.geometry_revision:
            checked=subprocess.check_output(['git','rev-parse','--verify',a.geometry_revision+'^{commit}'],cwd=repo,text=True).strip()
            if checked!=a.geometry_revision:raise ValueError('Full comparison geometry commit required')
            current=subprocess.check_output(['git','show',checked+':'+name],cwd=repo)
            if hashlib.sha256(current).hexdigest()!=want:raise ValueError('Geometry input differs from comparison revision: '+name)
    for name,want in expected.get('artifact_sha256',{}).items():
        if hashlib.sha256((a.compact.parent/name).read_bytes()).hexdigest()!=want:raise ValueError('Changed exported artifact: '+name)
    if a.library_sha256 and hashlib.sha256(a.library.read_bytes()).hexdigest()!=a.library_sha256:
        raise ValueError('Factory library differs from validated artifact')
    zoom=a.zoom_bounds or ([300.,460.,1834.,1946.] if a.name=='siw' else [379.,539.,2249.,2361.])
    if not all(math.isfinite(x) for x in zoom) or not zoom[0]<zoom[1] or not zoom[2]<zoom[3]:
        raise ValueError('Invalid finite zoom bounds')
    import ROOT as R,dd4hep
    R.gROOT.SetBatch(True)
    if R.gSystem.Load(str(a.library.resolve()))<0:raise RuntimeError('Factory load failed')
    d=dd4hep.Detector.getInstance();d.fromXML(str(a.compact.resolve()));g=d.manager();mm=float(dd4hep.mm)
    vols=list(g.GetListOfVolumes());size=max(v.GetNumber() for v in vols)+1;pal=R.std.vector('double')([255.]*(size*3));sensitive=R.std.vector('int')([0]*size);seen={}
    for v in vols:
        mat=v.GetMaterial();name=str(mat.GetName()) if mat else 'Assembly';sens=bool(dd4hep.Volume(v).isSensitive());sensitive[v.GetNumber()]=int(sens)
        if sens:color=(204,204,0)
        elif 'Tungsten' in name or name=='Lead' or name.endswith('_Lead'):color=(231,231,172)
        elif 'PCB' in name or 'G10' in name:color=(213,213,125)
        elif name in ('Air','Vacuum','Assembly') or name.endswith(('_Air','_Vacuum')):color=(255,255,255)
        elif name=='LAr' or name.endswith('_LAr'):color=(250,250,231)
        else:color=(215,219,202)
        for k in range(3):pal[v.GetNumber()*3+k]=color[k]
        seen[name+('|sensitive' if sens else '|passive')]=dict(material=name,rgb=color,sensitive=sens)
    if not R.gInterpreter.Declare(CPP):raise RuntimeError('Slice helper compilation failed')
    out=a.output;out.mkdir(parents=True,exist_ok=True);bounds=[-1150.,1150.,1490.,2916.];images={}
    for name,b,nx,ny,sub,angular in [('overview',bounds,1000,620,8,True),('zoom',zoom,800,560,2,False)]:
        pixels=R.NativeXY.render(g,mm,pal,*b,a.z,nx,ny,sub,angular);data=bytes(ord(v) if isinstance(v,str) else v for v in pixels);target=out/(a.name+'-'+name+'.png');png(target,nx,ny,data);images[name]=dict(file=target.name,bounds_mm=b,pixels=[nx,ny],subrows=sub,sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    rays={}
    for name,angle in [('boundary',math.pi/2-math.pi/16),('centre',math.pi/2),('near_minus',math.pi/2-math.pi/16-.001),('near_plus',math.pi/2-math.pi/16+.001)]:
        values=list(R.NativeXY.ray(g,mm,sensitive,angle,a.z,3100.));rays[name]=dict(phi_rad=angle,sensitive_segments=len(values)//3,sensitive_length_mm=sum(values[1::3]),first_sensitive_radius_mm=values[0] if values else None,last_sensitive_radius_mm=values[-3]+values[-2] if values else None)
    digest=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
    result=dict(status='PASS',source='Actual DD4hep placed-volume ROOT navigator; exact X boundaries, pixel-area X integration and Y subrows',model=a.name,z_mm=a.z,images=images,rays=rays,materials=seen,logical_volumes=len(vols),native=dict(ROOT=R.gROOT.GetVersion(),dd4hep_mm=mm),compact_sha256=digest(a.compact),library_sha256=digest(a.library),extractor_sha256=digest(Path(__file__)),cpp_sha256=hashlib.sha256(CPP.encode()).hexdigest(),source_revision=expected['execution']['commit'],expected_sha256=digest(expected_file),geometry_source_sha256=expected['source_sha256'],limits='Geometric transverse slice and navigator intersections, not energy-response performance; no transport.')
    result['drawing_geometry']=drawing_geometry(expected)
    result['checked_geometry_revision']=a.geometry_revision
    (out/(a.name+'-slice.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(model=a.name,rays=rays,images=images,volumes=len(vols))))

if __name__=='__main__':main()
