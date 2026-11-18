"""Compare native Si-W and restored1.8mmPb LAr slices at identical XY coordinates."""
import argparse
import base64
import hashlib
import html
import json
import math
from pathlib import Path


def validate(data, folder):
    for model in data.values():
        if model['z_mm'] != 0 or model['status'] != 'PASS':
            raise ValueError('Need successful native z=0 slices')
        for view in model['images'].values():
            if hashlib.sha256((folder/view['file']).read_bytes()).hexdigest() != view['sha256']:
                raise ValueError('Changed native image')
    for view in ('overview', 'zoom'):
        if data['siw']['images'][view]['bounds_mm'] != data['lar']['images'][view]['bounds_mm']:
            raise ValueError('Both native panels must use identical physical XY bounds')
    if data['siw']['rays']['boundary']['sensitive_segments'] != 0 or data['lar']['rays']['boundary']['sensitive_segments'] <= 0:
        raise ValueError('Boundary-ray illustration does not match the native result')
    c=data['lar']['drawing_geometry']
    for key,value in dict(lead_mm=1.8,planes=1248,sampling_inner_radius_mm=1772.8,
                          sampling_outer_radius_mm=2350.,warm_outer_radius_mm=2641.7,
                          inclination_deg=50.18).items():
        if not math.isclose(c[key],value,rel_tol=0,abs_tol=1e-8):
            raise ValueError('Wrong restored LAr variant: '+key)
    if not data['lar'].get('checked_geometry_revision') or data['lar']['checked_geometry_revision'] != data['siw'].get('checked_geometry_revision'):
        raise ValueError('Need one checked current geometry revision for both panels')


def draw(folder, output):
    data={n:json.loads((folder/(n+'-slice.json')).read_text()) for n in ('siw','lar')}
    validate(data,folder)
    output.mkdir(parents=True,exist_ok=True)
    ink,muted,red,line='#25312e','#53625b','#ac3328','#b9c2b9'
    s=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1800" height="1690" viewBox="0 0 1800 1690">',
       '<title>Si-W sector seam and restored1.8mmPb inclined LAr sampling</title>',
       '<desc>Native DD4hep XY slices at z=0, with identical overview and zoom coordinates. A geometric IP ray follows the Si-W structural seam and crosses sensitive inclined LAr gaps in the updated prototype. Raster geometry, vector annotations.</desc>',
       '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="'+red+'"/></marker></defs>',
       '<rect width="1800" height="1690" fill="white"/>']
    def text(x,y,t,size=20,color=ink,weight='normal',anchor='start'):
        s.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(t)}</text>')
    def ln(x,y,X,Y,color=line,width=1,dash=None,arrow=False):
        s.append(f'<line x1="{x:.3f}" y1="{y:.3f}" x2="{X:.3f}" y2="{Y:.3f}" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def rect(x,y,w,h,color,stroke='none'):
        s.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{color}" stroke="{stroke}"/>')
    def image(x,y,w,h,path):
        s.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" xlink:href="data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}"/>')
    def xy(x,y,b,px,py,w,h):
        return px+(x-b[0])/(b[1]-b[0])*w,py+(b[3]-y)/(b[3]-b[2])*h
    text(55,53,'Si–W sector seam versus inclined LAr sampling',35,weight='bold')
    text(55,91,'Updated LAr prototype: 1.8 mm Pb • 1248 periods • 50.18° inclination • native DD4hep placed solids at z = 0',21,muted)
    ln(55,116,1745,116)
    for i,name in enumerate(('siw','lar')):
        px,py,w,h=70+i*890,240.,780.,483.6
        j=data[name];b=j['images']['overview']['bounds_mm'];c=j['drawing_geometry']
        text(px,157,'Si–W barrel  |  unchanged comparison model' if name=='siw' else 'Restored LAr barrel  |  updated prototype',24,weight='bold')
        text(px,187,'One 22.5° sector + two neighbouring 11.25° half-sectors' if name=='siw' else 'The same 45° window of the inclined-period geometry',18,muted)
        if name=='siw':
            dimensions=f'Stack face-normal bounds: {c["stack_front_apothem_mm"]:g}–{c["stack_outer_apothem_mm"]:g} mm; {c["layers"]} layers'
        else:
            dimensions=f'Sampling R: {c["sampling_inner_radius_mm"]:g}–{c["sampling_outer_radius_mm"]:g} mm; warm outer R: {c["warm_outer_radius_mm"]:g} mm'
        text(px,215,dimensions,17,muted)
        image(px,py,w,h,folder/j['images']['overview']['file']);rect(px,py,w,h,'none',line)
        for x in (-1000,-500,0,500,1000):
            X,Y=xy(x,b[2],b,px,py,w,h);ln(X,Y,X,Y+6);text(X,Y+27,str(x),16,muted,anchor='middle')
        for y in (1500,2000,2500,2900):
            X,Y=xy(b[0],y,b,px,py,w,h);ln(X-6,Y,X,Y);text(X-10,Y+5,str(y),16,muted,anchor='end')
        text(px+w/2,py+h+54,'x [mm]   •   IP (0, 0) is below the view',17,muted,anchor='middle');text(px-37,py-10,'y [mm]',16,muted)
        limits=(c['stack_front_apothem_mm']-20,c['stack_outer_apothem_mm']+60) if name=='siw' else (c['warm_inner_radius_mm']-20,c['warm_outer_radius_mm']+30)
        for sign in (-1,1):
            angle=math.pi/2+sign*math.pi/16
            A=xy(limits[0]*math.cos(angle),limits[0]*math.sin(angle),b,px,py,w,h)
            B=xy(limits[1]*math.cos(angle),limits[1]*math.sin(angle),b,px,py,w,h)
            ln(*A,*B,red if sign==-1 else '#798579',1.5,'7 5',sign==-1)
        q=j['images']['zoom'];zb=q['bounds_mm'];A=xy(zb[0],zb[3],b,px,py,w,h);B=xy(zb[1],zb[2],b,px,py,w,h)
        rect(A[0],A[1],B[0]-A[0],B[1]-A[1],'none',red)
        text(px,814,'The structural seam stays aligned through the sampling stack.' if name=='siw' else 'Inclined sampling interrupts a straight projective corridor.',19,weight='bold')
        n=j['rays']['boundary']['sensitive_segments'];unit='Si' if name=='siw' else 'LAr'
        text(px,846,f'Same IP ray, φ = 78.75°: {n} sensitive {unit} path segments.',19,red)
        text(px,875,'Air seam, passive rails and sensor setbacks form the inactive band.' if name=='siw' else 'These guides are comparison angles, not LAr sector boundaries.',17,muted)
        text(px,930,'Si–W seam: tungsten, silicon and passive edge material' if name=='siw' else 'Same physical XY slice: lead, electrodes and active LAr gaps',21,weight='bold')
        zx,zy,zw,zh=px+40,960.,700.,490.
        image(zx,zy,zw,zh,folder/q['file']);rect(zx,zy,zw,zh,'none',line)
        low,high=zb[2],zb[3];angle=math.pi/16
        A=xy(low*math.tan(angle),low,zb,zx,zy,zw,zh);B=xy(high*math.tan(angle),high,zb,zx,zy,zw,zh)
        ln(*A,*B,red,1.8,'7 5',True)
        text(zx,zy+zh+28,'Identical 160 × 112 mm window and magnification',17,muted)
        ln(zx+zw-107.5,zy+zh+23,zx+zw-20,zy+zh+23,ink,3);text(zx+zw-64,zy+zh+47,'20 mm',15,muted,anchor='middle')
    for i,(color,label) in enumerate([('#cccc00','Sensitive Si / LAr'),('#e7e7ac','W / Pb absorber'),('#d5d57d','PCB / electrode'),('#d7dbca','Other passive solids'),('#fafae7','Passive LAr bath')]):
        x=55+i*345;rect(x,1560,24,14,color,line);text(x+35,1574,label,17,muted)
    text(55,1613,'Same axes, scale and zoom coordinates. Geometric ray only; path-segment counts are not sampling-layer counts or shower efficiency.',18,muted)
    text(55,1643,'Air/vacuum is white. Actual cryostat and services are retained. Native geometry is embedded raster; labels and guides are vector.',17,muted)
    text(55,1672,'Si–W '+data['siw']['source_revision'][:12]+' • LAr '+data['lar']['source_revision'][:12]+' • geometry bytes checked against '+data['lar']['checked_geometry_revision'][:12],15,muted)
    s.append('</svg>');target=output/'siw-restored-lar-sector-gap.svg';target.write_text('\n'.join(s)+'\n')
    report=dict(status='PASS',scope='Native DD4hep geometry comparison, identical physical XY bounds; no geometry or response change.',models=data,
                svg_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),annotation_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (output/'native-slice-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
    print(target)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--slices',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();draw(a.slices,a.output)
