"""Draw the tested Si-W staggering from its Python packing functions (no native runtime)."""
import argparse, hashlib, html, json, math, subprocess, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    repo=a.repo.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    expected='3ebafd340b0e084c5e42e57123de115e3f489244'
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    if actual!=expected:p.error('Use a clean source worktree at '+expected+'; this drawing documents the tested PR136/137 prototype.')
    sys.path[:0]=[str(repo/'tools/calorimeter_hardware'),str(repo/'software/analysis/calorimeter_digitization')]
    from barrel_layout import build as barrel_build
    from staggered_geometry import PHASES, tangent_boards, panel_rows
    from edge_layout import build as edge_build, pack
    b,_=barrel_build();eb,el,_=edge_build();ec=b['ecal']
    recorded=json.loads((repo/'docs/validation/ecal-staggering/geometry-and-run.json').read_text())
    assert [list(x) for x in PHASES]==recorded['phases_mm']
    assert hashlib.sha256((repo/'software/analysis/calorimeter_digitization/staggered_geometry.py').read_bytes()).hexdigest()==recorded['recipe_sha256']
    assert b['board_pitch_mm']==96 and b['board_size_mm']==94 and b['layer_pitch_mm']==10.9
    assert all(x['columns']==6 for x in b['layers'][:4])
    edge=[]
    for i,(u,r) in enumerate(PHASES):
        q=pack(eb['config'],ec,eb['outer_polygon_mm'],el['edges']['phase_mm']+r,True,tangent_phase_mm=u,inner_partial_row=bool(r))
        assert len(q['modules'])==recorded['endcap']['families'][i]['module_count']
        edge.append(q)
    C={'ink':'#202b2b','muted':'#52605e','line':'#89948b','active':'#cccc00','wafer':'#ecec99','pcb':'#f5f5cf','W':'#e0e0a1','box':'#f7f8f3','red':'#a33c2d'}
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1580" viewBox="0 0 1800 1580">',
       '<title>Staggered silicon–tungsten ECAL: tested four-layer prototype</title>',
       '<desc>True barrel module masks and four endcap packing families, plus a scaled layer cutaway. Internal module gaps shift by half the 96 mm pitch; full-depth sector seams remain.</desc>',
       '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse"><path d="M0,0 L7,3.5 L0,7 Z" fill="#52605e"/></marker></defs>',
       '<rect width="1800" height="1580" fill="white"/>']
    def text(x,y,t,size=19,fill=None,weight='normal',anchor='start'):
        s.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" fill="{fill or C["ink"]}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(str(t))}</text>')
    def rect(x,y,w,h,fill,stroke='none',sw=1,rx=0):s.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def line(x,y,X,Y,color=None,sw=1,dash=None,arrow=False):
        s.append(f'<line x1="{x:.3f}" y1="{y:.3f}" x2="{X:.3f}" y2="{Y:.3f}" stroke="{color or C["line"]}" stroke-width="{sw}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def poly(points,fill,stroke=None,sw=.5):s.append('<polygon points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in points)+f'" fill="{fill}" stroke="{stroke or C["line"]}" stroke-width="{sw}"/>')
    def dim(x,y,X,Y,label,tx=None,ty=None):
        line(x,y,X,Y,C['muted'],1,arrow=True);text((x+X)/2 if tx is None else tx,(y+Y)/2-8 if ty is None else ty,label,17,C['muted'],anchor='middle')
    def board(cx,cy,w,h,k):
        rect(cx-w*k/2,cy-h*k/2,w*k,h*k,C['pcb'],C['line'],.8)
        rect(cx-(w-4)*k/2,cy-(h-4)*k/2,(w-4)*k,(h-4)*k,C['wafer'])
        rect(cx-(w-6)*k/2,cy-(h-6)*k/2,(w-6)*k,(h-6)*k,C['active'])
    text(58,62,'Staggered Si–W ECAL',38,weight='bold')
    text(58,99,'Tested physical prototype • 48 sampling layers • four-layer module pattern repeated 12 times',22,C['muted'])
    rect(1510,38,230,40,C['box'],C['line'],rx=9);text(1625,65,'PROTOTYPE',20,weight='bold',anchor='middle')
    line(58,121,1740,121,C['line'])
    text(58,163,'A  |  Barrel module pattern',25,weight='bold')
    text(58,193,'Front views of the same central patch; u is tangential, z is along the beam.',18,C['muted'])
    k=.57;u0=-287;zmax=216;zmin=-216;patch_w=574*k;patch_h=(zmax-zmin)*k
    for i,(up,zp) in enumerate(PHASES):
        x=58+(i%2)*430;y=218+(i//2)*356
        rect(x,y,404,334,C['box'],rx=12)
        text(x+18,y+30,f'Layer {i+1}   (Δu, Δz) = ({up:g}, {zp:g}) mm',19,weight='bold')
        px=x+39;py=y+55
        s.append(f'<clipPath id="patch{i}"><rect x="{px}" y="{py}" width="{patch_w}" height="{patch_h}"/></clipPath><g clip-path="url(#patch{i})">')
        # Actual common-z positions include inherited +/-96 mm slab movement.
        layer=b['layers'][i];panel=layer['panels'][4];rows,actual,*_=panel_rows(panel,zp)
        cols=tangent_boards(layer['columns'],bool(up))
        for z in rows:
            for u,fam,_ in cols:
                w=46 if fam=='half_tangent' else 94
                if z+47>=zmin and z-47<=zmax:board(px+(u-u0)*k,py+(zmax-z)*k,w,94,k)
        s.append('</g>')
        rect(px,py,patch_w,patch_h,'none',C['line'],.7)
        text(px,py+patch_h+23,'−287',14,C['muted'],anchor='middle');text(px+patch_w,py+patch_h+23,'+287 mm',14,C['muted'],anchor='middle')
        line(px+patch_w+15,py+64,px+patch_w+15,py+13,C['muted'],1.1,arrow=True);text(px+patch_w+23,py+27,'z',17)
        line(px+patch_w/2-28,py+patch_h+16,px+patch_w/2+28,py+patch_h+16,C['muted'],1,arrow=True);text(px+patch_w/2,py+patch_h+35,'u',17,anchor='middle')
    text(58,954,'Same 574 mm PCB span: 6 full boards → 5 full + 2 narrow edge boards.',18,C['muted'])
    text(58,980,'White channels are inactive module gaps; the four masks do not have aligned gaps.',18,C['muted'])
    text(948,163,'B  |  Through the sampling stack',25,weight='bold')
    text(948,193,'u–depth cut at z = 24 mm; depth is enlarged ×5 relative to u.',18,C['muted'])
    X=1020;Y=234;ku=.96;kr=4.8;W=574*ku
    for i in range(4):
        ly=Y+i*b['layer_pitch_mm']*kr
        rect(X,ly,W,ec['absorber_mm']*kr,C['W'],C['line'],.6)
        rect(X,ly+(ec['absorber_mm']+.2)*kr,W,7.8*kr,C['box'])
        layer=b['layers'][i]
        for u,fam,_ in tangent_boards(layer['columns'],bool(PHASES[i][0])):
            w=46 if fam=='half_tangent' else 94;active=w-6
            rect(X+(u+287-w/2)*ku,ly+(ec['absorber_mm']+ec['pcb_front_mm'])*kr,w*ku,ec['pcb_mm']*kr,C['pcb'],C['line'],.5)
            rect(X+(u+287-active/2)*ku,ly+(ec['absorber_mm']+ec['sensor_center_z_mm']-ec['sensor_mm']/2)*kr,active*ku,ec['sensor_mm']*kr,C['active'],C['ink'],.4)
        text(X-20,ly+17,f'L{i+1}',16,C['muted'],anchor='end')
    ray=X+287*ku;line(ray,Y-17,ray,Y+4*10.9*kr+8,C['red'],1.7,'6 4',True)
    text(ray+18,Y-9,'example track at a module gap',17,C['red'])
    dim(X+W+35,Y,X+W+35,Y+10.9*kr,'10.9 mm',X+W+105,Y+29)
    text(948,493,'1.9 mm tungsten',18);rect(948,508,27,10,C['W'],C['line'],.6)
    text(990,519,'absorber',17,C['muted']);rect(1173,508,27,10,C['active'],C['ink'],.5);text(1215,519,'0.5 mm sensitive Si',17,C['muted'])
    text(948,551,'The track crosses active Si in L2/L4 instead of staying in a module gap.',18,C['muted'])
    text(948,579,'PCB shown; skins, guards, ASICs, cooling and films simplified in this cut.',17,C['muted'])
    text(948,636,'C  |  Full and narrow edge modules',25,weight='bold')
    bx=1022;by=754;bk=1.37;board(bx,by,94,94,bk);board(1297,by,46,94,bk)
    dim(bx-47*bk,by-47*bk-17,bx+47*bk,by-47*bk-17,'94 mm PCB')
    dim(1297-23*bk,by-47*bk-17,1297+23*bk,by-47*bk-17,'46 mm')
    text(bx,by+89,'Full',18,weight='bold',anchor='middle');text(1297,by+89,'Narrow',18,weight='bold',anchor='middle')
    text(1415,716,'PCB',18,weight='bold');text(1415,743,'94 × 94 / 46 × 94 mm',18,C['muted'])
    text(1415,781,'Silicon blank',18,weight='bold');text(1415,808,'90 × 90 / 42 × 90 mm',18,C['muted'])
    text(1415,846,'Sensitive area',18,weight='bold');text(1415,873,'88 × 88 / 40 × 88 mm',18,C['muted'])
    text(948,921,'2 mm PCB margin + 1 mm Si guard per edge; 2 mm between PCBs.',18,C['muted'])
    text(948,949,'Active-to-active gap: 8 mm. Readout: four / two ASICs (not drawn).',18,C['muted'])
    text(948,980,'Short end slabs: 24 mm axial shift; full slabs: 48 mm away from the bay.',18,C['muted'])
    line(58,1010,1740,1010,C['line'])
    text(58,1050,'D  |  Endcap: four physical wedge families',25,weight='bold')
    text(58,1079,'Actual packed masks, one of sixteen 22.5° sectors. Half-pitch offsets are tangential / radial.',18,C['muted'])
    for i,q in enumerate(edge):
        cx=210+i*425;ey=1402;ke=.137
        text(cx,1119,f'({PHASES[i][0]:g}, {PHASES[i][1]:g}) mm',19,weight='bold',anchor='middle')
        conv=lambda x,y:(cx+y*ke,ey-(x-130)*ke)
        poly([conv(x,y) for x,y in q['face_mm']],C['box'],C['line'],.8)
        for m in q['modules']:
            ox,oy=m['center_mm']
            for key,color in [('board',C['pcb']),('sensor',C['wafer']),('active',C['active'])]:poly([conv(x+ox,y+oy) for x,y in m[key]],color,C['line'] if key=='board' else color,.25)
        text(cx,1432,f'{len(q["modules"])} modules / sector-layer',17,C['muted'],anchor='middle')
    text(58,1476,'Internal module gaps are staggered. The sixteen full-depth sector seams and service reservations remain.',19,weight='bold')
    text(58,1507,'Also retained: ±96 mm mechanical slab staggering, absorber planes, carrier envelopes and cooling.',18,C['muted'])
    rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    text(58,1549,f'Geometry: PR136/137 tested prototype • DES-030 / DES-031 • source {rev[:12]} • plan views to scale; supports omitted.',15,C['muted'])
    s.append('</svg>');target=out/'staggered-siw-layout.svg';target.write_text('\n'.join(s)+'\n')
    sources=['software/analysis/calorimeter_digitization/staggered_geometry.py','tools/calorimeter_hardware/barrel_layout.py','tools/calorimeter_hardware/edge_layout.py','tools/calorimeter_hardware/barrel.json','tools/calorimeter_hardware/cassettes.json','tools/calorimeter_hardware/edge_sensors.json','docs/validation/ecal-staggering/geometry-and-run.json']
    for f in sources:
        assert (repo/f).read_bytes()==subprocess.check_output(['git','show',expected+':'+f],cwd=repo), 'Dirty frozen drawing input: '+f
    report=dict(status='PROTOTYPE illustration, no geometry change or new response claim',source_revision=rev,phases_mm=PHASES,barrel_columns_first_four=[x['columns'] for x in b['layers'][:4]],endcap_modules=[len(x['modules']) for x in edge],source_sha256={f:hashlib.sha256((repo/f).read_bytes()).hexdigest() for f in sources},drawing_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (out/'staggered-siw-layout.provenance.json').write_text(json.dumps(report,indent=2)+'\n');print(target)

if __name__=='__main__':main()
