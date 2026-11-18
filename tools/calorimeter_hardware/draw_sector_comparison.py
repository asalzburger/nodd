"""Annotate matched native DD4hep XY slices, preserving their geometry pixels."""
import argparse,base64,hashlib,html,json,math,shutil
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--slices',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 data={n:json.loads((a.slices/(n+'-slice.json')).read_text()) for n in ('siw','lar')}
 assert all(j['z_mm']==0 for j in data.values())
 assert data['siw']['images']['overview']['bounds_mm']==data['lar']['images']['overview']['bounds_mm']
 assert data['siw']['rays']['boundary']['sensitive_segments']==0
 assert data['lar']['rays']['boundary']['sensitive_segments']>0
 for j in data.values():
  for v in j['images'].values():assert hashlib.sha256((a.slices/v['file']).read_bytes()).hexdigest()==v['sha256']
 ink='#25312e';muted='#53625b';red='#ac3328';line='#b9c2b9'
 s=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1800" height="1580" viewBox="0 0 1800 1580">','<title>Sector boundary: current Si-W and ALLEGRO-style DD4hep barrel models</title>','<desc>Matched native ROOT navigator XY material/sensitivity slices at z=0. Si-W sector4 plus two neighboring half-sectors, and the same45degree view of the current continuous inclined-period LAr model. Geometry images are embedded native rasters; annotations are vector.</desc>','<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="'+red+'"/></marker></defs>','<rect width="1800" height="1580" fill="white"/>']
 def text(x,y,t,size=20,color=ink,weight='normal',anchor='start'):s.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(t)}</text>')
 def ln(x,y,X,Y,color=line,width=1,dash=None,arrow=False):s.append(f'<line x1="{x:.3f}" y1="{y:.3f}" x2="{X:.3f}" y2="{Y:.3f}" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
 def rect(x,y,w,h,color,stroke='none'):s.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{color}" stroke="{stroke}"/>')
 def image(x,y,w,h,path):s.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" xlink:href="data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}"/>')
 def conv(x,y,b,px,py,w,h):return px+(x-b[0])/(b[1]-b[0])*w,py+(b[3]-y)/(b[3]-b[2])*h
 text(55,54,'Where does a sector boundary become a blind corridor?',35,weight='bold')
 text(55,91,'Our current DD4hep models • native placed solids and sensitivity • XY at z = 0 mm • identical axes and scale',21,muted)
 ln(55,115,1745,115)
 for i,name in enumerate(('siw','lar')):
  px=70+i*890;py=205;w=780.;h=483.6;j=data[name];b=j['images']['overview']['bounds_mm']
  text(px,158,'Si–W barrel  |  LAYOUT-001' if name=='siw' else 'Our ALLEGRO-style LAr barrel  |  LAYOUT-002',24,weight='bold')
  text(px,187,'One full 22.5° sector + two neighbouring 11.25° half-sectors' if name=='siw' else 'Same 45° XY window; current inclined-period model',18,muted)
  image(px,py,w,h,a.slices/j['images']['overview']['file']);rect(px,py,w,h,'none',line)
  for x in (-1000,-500,0,500,1000):
   X,Y=conv(x,b[2],b,px,py,w,h);ln(X,Y,X,Y+6);text(X,Y+27,str(x),16,muted,anchor='middle')
  for y in (1500,2000,2500,2900):
   X,Y=conv(b[0],y,b,px,py,w,h);ln(X-6,Y,X,Y);text(X-10,Y+5,str(y),16,muted,anchor='end')
  text(px+w/2,py+h+54,'x [mm]     •     IP (0, 0) is below this view',17,muted,anchor='middle');text(px-37,py-10,'y [mm]',16,muted)
  for sign in (-1,1):
   ang=math.pi/2+sign*math.pi/16;ranges=(1680,2310) if name=='siw' else (2120,2870)
   A=conv(ranges[0]*math.cos(ang),ranges[0]*math.sin(ang),b,px,py,w,h);B=conv(ranges[1]*math.cos(ang),ranges[1]*math.sin(ang),b,px,py,w,h)
   ln(*A,*B,red if sign==-1 else '#798579',1.4,'7 5',sign==-1)
  zoom=j['images']['zoom']['bounds_mm'];A=conv(zoom[0],zoom[3],b,px,py,w,h);B=conv(zoom[1],zoom[2],b,px,py,w,h);rect(A[0],A[1],B[0]-A[0],B[1]-A[1],'none',red)
  text(px,py+h+89,'Physical sector seams align through all 48 sampling layers.' if name=='siw' else 'Dashed rays are comparison guides—not module boundaries.',19,weight='bold')
  n=j['rays']['boundary']['sensitive_segments'];text(px,py+h+119,('Shown boundary ray: ' if name=='siw' else 'Shown comparison ray: ')+f'{n} sensitive '+('Si' if name=='siw' else 'LAr')+' path segments.',19,red)
  text(px,py+h+147,'White seam + passive rails + sensor setback: a wider inactive band.' if name=='siw' else 'The ray crosses real inclined absorbers, electrodes and active gaps.',17,muted)
  zx=px+40;zy=920.;zw=700.;zh=490.;q=j['images']['zoom'];zb=q['bounds_mm']
  text(px,891,'Enlarged native slice at the sector boundary' if name=='siw' else 'Enlarged native slice at the same comparison angle',22,weight='bold')
  image(zx,zy,zw,zh,a.slices/q['file']);rect(zx,zy,zw,zh,'none',line)
  low,high=zb[2],zb[3];ang=math.pi/16;A=conv(low*math.tan(ang),low,zb,zx,zy,zw,zh);B=conv(high*math.tan(ang),high,zb,zx,zy,zw,zh);ln(*A,*B,red,1.8,'7 5',True)
  text(zx,zy+zh+28,'160 × 112 mm window; same magnification in both panels',17,muted)
  ln(zx+zw-107.5,zy+zh+23,zx+zw-20,zy+zh+23,ink,3);text(zx+zw-64,zy+zh+47,'20 mm',15,muted,anchor='middle')
 legend=[('#cccc00','Sensitive Si / LAr'),('#e7e7ac','W / Pb absorber'),('#d5d57d','PCB / electrode'),('#d7dbca','Other passive solids'),('#fafae7','Passive LAr bath')]
 for i,(color,label) in enumerate(legend):
  x=55+i*345;rect(x,1485,24,14,color,line);text(x+35,1499,label,17,muted)
 text(55,1537,'Native geometry illustration—not an energy-resolution claim. Air/vacuum is white; cryostat, services and passive supports are retained.',18,muted)
 text(55,1564,'Source '+data['siw']['source_revision'][:12]+' • real-wedges / real-periods component exports • boundary counts include volume segmentation, not sampling-layer counts.',15,muted)
 s.append('</svg>');target=a.output/'siw-allegro-sector-gap.svg';target.write_text('\n'.join(s)+'\n')
 report=dict(status='PASS',scope='Matched current native DD4hep XY model slices; embedded navigator-derived rasters, vector annotations. No replacement schematic solids.',models=data,svg_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),annotation_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (a.output/'native-slice-provenance.json').write_text(json.dumps(report,indent=2)+'\n');print(target)

if __name__=='__main__':main()
