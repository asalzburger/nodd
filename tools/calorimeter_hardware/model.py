"""DES028 isolated physical cassette inventories; units mm, g, W, SI services.

Material and geometry choices are centralized and documented in DES028. Active
and passive silicon are distinct; packages contain their own constituent ledger.
"""
import hashlib,json,math,sys
from pathlib import Path
from collections import Counter,defaultdict
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT/'tools/pixel_barrel_dd4hep'))
from materials import Materials
I=[[1,0,0],[0,1,0],[0,0,1]]
TUBE_Y=[[1,0,0],[0,0,1],[0,-1,0]]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def materials(c):
    m=Materials(dict(coolant_density_g_cm3=1,cfrp_carbon_mass_fraction=.7,module=dict(flex_copper_coverage=.5)),dict(density_g_cm3=c['stock_densities_g_cm3']))
    m.add('Aluminium',2.7,{'Al':1});m.add('Water',1,{'H':2,'O':1},atoms=True)
    m.add('Steel235',7.85,c['steel_recipe']);m.add('StainlessProxy',7.9,c['stainless_recipe'])
    m.add('TungstenDens24',17.8,{'W':.93,'Ni':.061,'Fe':.009})
    m.add('Quartz',2.2,{'Si':1,'O':2},atoms=True)
    m.add('G10',1.7,{'Cl':.08,'Quartz':.773,'Epoxy':.147})
    m.add('Polystyrene',1.032,{'C':19,'H':21},atoms=True)
    m.add('PET',1.4,{'C':10,'H':8,'O':4},atoms=True)
    q=c['package_recipes']['ECalPackage'];volume=math.prod(q['size_mm'])
    die=math.prod(c['ecal']['asic_die_xy_mm'])*q['die_mm'];cu=q['copper_volume_fraction']*volume
    if die+cu>=volume:raise ValueError('package constituents exceed envelope')
    m.effective('ECalPackage',{'Silicon':die,'Copper':cu,'Epoxy':volume-die-cu},volume)
    for name in ('HCalPackage','SiPMPackage'):
        fractions=c['package_recipes'][name]['volume_fractions']
        if any(v<=0 for v in fractions.values()) or not math.isclose(sum(fractions.values()),1):raise ValueError('package normalization')
        m.effective(name,fractions,1)
    return m

class Cassette:
    def __init__(self,c,kind,m,common):self.config=c;self.kind=kind;self.m=m;self.parts=[];self.common=common
    def add(self,name,role,mat,center,kind,dims,sensor=None,cuts=None,frame=I,owner='cassette'):
        v=capacity(kind,dims)
        cuts=cuts or [];validate_cut(kind,dims,cuts)
        for cut in cuts:v-=capacity(cut['kind'],cut['dimensions_mm'])
        if v<=0:raise ValueError('invalid exclusive capacity')
        p=dict(name=self.kind+'_'+name,role=role,material=mat,center_mm=center,frame=frame,
               shape_kind=kind,dimensions_mm=dims,cuts=cuts,volume_mm3=v,
               mass_g=v*self.m.recipes[mat]['density_g_cm3']/1000,owner=owner)
        if sensor is not None:p['sensor']=sensor
        self.parts.append(p);return p
    def box(self,name,role,mat,center,size,**kw):return self.add(name,role,mat,center,'box',dict(zip(('sx','sy','sz'),size)),**kw)
    def plane(self,name,role,mat,z,t,w=None,h=None,**kw):return self.box(name,role,mat,[0,0,z],[w or self.config['width_mm'],h or self.config['height_mm'],t],**kw)
    def rails(self):
        c=self.config;w,h,d=[c[k] for k in ('width_mm','height_mm','body_depth_mm')]
        r=self.common['rail_mm']
        for side in (-1,1):
            self.box('u_rail'+str(side),'frame','Aluminium',[side*(w-r)/2,0,d/2],[r,h,d])
            ports=[];diameter=2*self.common['tube_outer_radius_mm']
            for tube_x in c['tube_x_mm']:
                cut=cut_box([diameter,r,diameter]);cut['center_mm']=[tube_x,0,c['tube_z_mm']-d/2];ports.append(cut)
            self.box('v_rail'+str(side),'frame','Aluminium',[0,side*(h-r)/2,d/2],[w-2*r,r,d],cuts=ports)
    def tube(self,name,x,z):
        c=self.config;length=c['height_mm']
        for role,mat,r0,r1 in [('pipe','Titanium',self.common['tube_inner_radius_mm'],self.common['tube_outer_radius_mm']),('coolant',self.common['coolant'],0,self.common['tube_inner_radius_mm'])]:
            self.add(name+'_'+role,role,mat,[x,0,z],'tube',dict(rmin=r0,rmax=r1,length=length),frame=TUBE_Y)


def validate_config(c):
    for key in ('tube_outer_radius_mm','tube_inner_radius_mm','rail_mm','LV_V','coolant_rise_K','coolant_heat_capacity_J_kg_K'):
        if not math.isfinite(c[key]) or c[key]<=0:raise ValueError('positive finite '+key)
    if not 0<c['converter_efficiency']<=1 or c['tube_inner_radius_mm']>=c['tube_outer_radius_mm']:raise ValueError('services normalization')
    for kind in ('ecal','hcal'):
        q=c[kind]
        for key in ('width_mm','height_mm','body_depth_mm','absorber_mm','pcb_mm','pcb_copper_equivalent_mm','bias_V'):
            if not math.isfinite(q[key]) or q[key]<=0:raise ValueError('positive finite '+kind+' '+key)
        if q['pcb_copper_equivalent_mm']>=q['pcb_mm']:raise ValueError('PCB normalization')
        if q['asic_continuous_W_channel']<=0 or q['interface_W']<0:raise ValueError('power budget')
    e=c['ecal'];h=c['hcal'];cells=e['sensor_active_mm']/e['pitch_mm']
    if not cells.is_integer() or not 0<e['sensor_active_mm']<e['sensor_outer_mm']:raise ValueError('ECAL active/guard/readout fit')
    if 4*cells**2!=e['asic_rows']**2*e['asic_channels']:raise ValueError('ECAL channel ownership')
    if h['tile_rows']**2!=len(h['asic_centers_xy_mm'])*h['asic_channels']:raise ValueError('HCAL channel ownership')
    if not 0<h['recess_depth_mm']<h['tile_mm'] or h['tile_active_mm']+2*h['wrap_mm']>=h['tile_pitch_mm']:raise ValueError('HCAL tile/wrapper fit')
    if math.hypot(*h['tile_parts'][0]['size_mm'][:2])/2>=h['recess_radius_mm']:raise ValueError('SiPM recess fit')
    if max(e['system_id'],h['system_id'])>=256 or e['system_id']==h['system_id'] or h['tile_rows']**2>256:raise ValueError('identifier capacity')

def extent(kind,d):
    if kind=='box':return [d[k]/2 for k in ('sx','sy','sz')]
    if kind=='tube':return [d['rmax'],d['rmax'],d['length']/2]
    raise ValueError('unsupported primitive')

def validate_cut(kind,d,cuts):
    # Restricted CSG contract: contained, nonoverlapping unrotated cutters.
    # This proves subtraction of capacities is exact, independent of ROOT's
    # stochastic composite Capacity(). Touching cutter boundaries are allowed.
    e=extent(kind,d)
    for cut in cuts:
        q=cut['dimensions_mm'];capacity(cut['kind'],q);b=extent(cut['kind'],q)
        if any(abs(v)+a>r+1e-10 for v,a,r in zip(cut['center_mm'],b,e)):raise ValueError('cutter not contained')
    for i,a in enumerate(cuts):
        for b in cuts[i+1:]:
            if all(abs(v-w)<u+t-1e-10 for v,w,u,t in zip(a['center_mm'],b['center_mm'],extent(a['kind'],a['dimensions_mm']),extent(b['kind'],b['dimensions_mm']))):raise ValueError('cutters overlap')

def capacity(kind,d):
    if any(not math.isfinite(v) for v in d.values()):raise ValueError('nonfinite shape')
    if kind=='box' and any(v<=0 for v in d.values()):raise ValueError('nonpositive box')
    if kind=='tube' and not (0<=d['rmin']<d['rmax'] and d['length']>0):raise ValueError('invalid tube')
    if kind=='box':return d['sx']*d['sy']*d['sz']
    if kind=='tube':return math.pi*(d['rmax']**2-d['rmin']**2)*d['length']
    raise ValueError('unsupported primitive')

def cut_box(size):return dict(kind='box',center_mm=[0,0,0],dimensions_mm=dict(zip(('sx','sy','sz'),size)))
def cut_tube(r,L,z):return dict(kind='tube',center_mm=[0,0,z],dimensions_mm=dict(rmin=0,rmax=r,length=L))

def add_hardware(x,config):
    c=x.config;r=config['rail_mm']
    for p in c['planes']:
        x.plane(p['name'],p['role'],p['material'],p['center_z_mm'],p['thickness_mm'],w=c['width_mm']-2*r,h=c['height_mm']-2*r)
    for p in c['service_parts']:x.box(p['name'],p['role'],p['material'],p['center_mm'],p['size_mm'])
    for i,u in enumerate(c['tube_x_mm']):x.tube('pipe'+str(i),u,c['tube_z_mm'])
    x.rails()

def add_pcb(x,c,cx=0):
    t=c['pcb_mm']-c['pcb_copper_equivalent_mm'];z=c['pcb_front_mm'];w=c['pcb_width_mm']
    if t<=0:raise ValueError('PCB copper exceeds board')
    x.box('PCB_G10','pcb','G10',[cx,0,z+t/2],[w,w,t])
    x.box('PCB_Cu','pcb','Copper',[cx,0,z+t+c['pcb_copper_equivalent_mm']/2],[w,w,c['pcb_copper_equivalent_mm']])

def add_asics(x,c,centers):
    for i,(u,v) in enumerate(centers):
        for p in c['asic_stack']:
            x.box(f'a{i}_'+p['name'],p['role'],p['material'],[u,v,p['center_z_mm']],c['asic_package_xy_mm']+[p['thickness_mm']])

def build_ecal(config,m):
    c=config['ecal'];x=Cassette(c,'ecal',m,config);cx=c['ASU_center_x_mm']
    x.plane('absorber','absorber','TungstenDens24',-c['absorber_mm']/2,c['absorber_mm'],owner='sector')
    for i,(a,b) in enumerate(((-1,-1),(-1,1),(1,-1),(1,1))):
        u=cx+a*(c['sensor_outer_mm']+c['sensor_gap_mm'])/2;v=b*(c['sensor_outer_mm']+c['sensor_gap_mm'])/2
        for p in c['sensor_layers']:x.box(f's{i}_'+p['name'],p['name'],p['material'],[u,v,p['center_z_mm']],[c['sensor_outer_mm']]*2+[p['thickness_mm']])
        active=[c['sensor_active_mm']]*2+[c['sensor_mm']];outer=[c['sensor_outer_mm']]*2+[c['sensor_mm']]
        x.box(f's{i}_active','sensitive','Silicon',[u,v,c['sensor_center_z_mm']],active,sensor=i)
        x.box(f's{i}_guard','sensor_edge','Silicon',[u,v,c['sensor_center_z_mm']],outer,cuts=[cut_box(active)])
    add_pcb(x,c,cx)
    n=c['asic_rows'];add_asics(x,c,[(cx+(i%n-(n-1)/2)*c['asic_pitch_mm'],(i//n-(n-1)/2)*c['asic_pitch_mm']) for i in range(n*n)])
    add_hardware(x,config);return x

def build_hcal(config,m):
    c=config['hcal'];x=Cassette(c,'hcal',m,config)
    x.plane('absorber','absorber','Steel235',-c['absorber_mm']/2,c['absorber_mm'],owner='sector')
    n=c['tile_rows'];t=c['tile_mm'];w=c['tile_active_mm'];wrap=c['wrap_mm'];d=c['recess_depth_mm'];r=c['recess_radius_mm']
    for i in range(n*n):
        u=(i%n-(n-1)/2)*c['tile_pitch_mm'];v=(i//n-(n-1)/2)*c['tile_pitch_mm'];z=c['tile_center_z_mm']
        core=[w,w,t];outer=[w+2*wrap,w+2*wrap,t+2*wrap]
        x.box(f't{i}_active','sensitive','Polystyrene',[u,v,z],core,sensor=i,cuts=[cut_tube(r,d,(t-d)/2)])
        x.box(f't{i}_wrap','reflector','PET',[u,v,z],outer,cuts=[cut_box(core),cut_tube(r,wrap,(t+wrap)/2)])
        for p in c['tile_parts']:x.box(f't{i}_'+p['name'],p['role'],p['material'],[u,v,p['center_z_mm']],p['size_mm'])
    add_pcb(x,c);add_asics(x,c,c['asic_centers_xy_mm']);add_hardware(x,config);return x

def ledger(x,config):
    totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    for p in x.parts:
        for k in ('volume_mm3','mass_g'):totals[p['material']][k]+=p[k]
    c=x.config;n=4*round(c['sensor_active_mm']/c['pitch_mm'])**2 if x.kind=='ecal' else c['tile_rows']**2
    lv=(n*c['asic_continuous_W_channel']+c['interface_W'])/config['converter_efficiency']
    hv=n*c['bias_V']*c.get('leakage_A_channel',c.get('dark_current_A_channel'))
    return dict(name=x.kind,system_id=c['system_id'],parts=x.parts,counts=dict(Counter(p['role'] for p in x.parts)),
                material_totals=dict(totals),mass_g=sum(p['mass_g'] for p in x.parts),
                cassette_mass_g=sum(p['mass_g'] for p in x.parts if p['owner']=='cassette'),channels=n,
                sensitive_count=sum('sensor' in p for p in x.parts),
                power=dict(duty=1.,LV_input_W=lv,LV_input_A=lv/config['LV_V'],bias_W=hv,
                           total_heat_W=lv+hv,water_g_s=(lv+hv)/config['coolant_heat_capacity_J_kg_K']/config['coolant_rise_K']*1000),
                width_mm=c['width_mm'],height_mm=c['height_mm'],body_depth_mm=c['body_depth_mm'],absorber_mm=c['absorber_mm'],
                cell_pitch_mm=c.get('pitch_mm',c.get('tile_pitch_mm')),cell_offset_mm=c.get('pitch_mm',0)/2)


def build(config=None):
    c=config or json.loads((ROOT/'tools/calorimeter_hardware/cassettes.json').read_text());validate_config(c);m=materials(c)
    out=dict(status='PROTOTYPE / DRAFT',config=c,materials=m.recipes,
             units=[ledger(build_ecal(c,m),c),ledger(build_hcal(c,m),c)],
             source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),ROOT/'tools/calorimeter_hardware/cassettes.json',ROOT/'tools/pixel_barrel_dd4hep/materials.py',ROOT/'detector/config/elements.json')})
    for u in out['units']:
        for p in u['parts']:
            e=extent(p['shape_kind'],p['dimensions_mm']);bounds=[sum(abs(p['frame'][i][j])*e[i] for i in range(3)) for j in range(3)]
            if abs(p['center_mm'][0])+bounds[0]>u['width_mm']/2+1e-8 or abs(p['center_mm'][1])+bounds[1]>u['height_mm']/2+1e-8:raise ValueError('cassette lateral containment')
            lo=-u['absorber_mm'] if p['owner']=='sector' else 0
            if p['center_mm'][2]-bounds[2]<lo-1e-8 or p['center_mm'][2]+bounds[2]>u['body_depth_mm']+1e-8:raise ValueError('cassette depth containment')
    return out,m
