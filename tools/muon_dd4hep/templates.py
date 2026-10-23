"""Centred source shapes and proven phi/z recurrences; no geometry repacking.

All grouping uses an unrounded source representative within 1e-12 metres.
Recurrences are accepted only after expansion reproduces every original prism.
"""
from __future__ import annotations

from collections import Counter
from decimal import Context, Decimal, localcontext
from functools import lru_cache
import math
import re
import xml.etree.ElementTree as ET

MATCH_M = 1e-12
TAU = 2*math.pi
DECIMAL_CONTEXT = Context(prec=60)
PI = Decimal("3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986")


@lru_cache(maxsize=1024)
def sincos(phi):
    """Deterministic binary64 trig for export, independent of platform libm.

    Evaluate the Taylor series at 60 decimal digits before converting to float.
    Range reduction keeps the argument within pi; 90 terms suffice there.
    This is serialization arithmetic, not a change to geometry tolerances.
    """
    with localcontext(DECIMAL_CONTEXT):
        x=Decimal.from_float(phi)%(2*PI)
        if x>PI:x-=2*PI
        if x<-PI:x+=2*PI
        square=x*x
        sine=st=x;cosine=ct=Decimal(1)
        for n in range(1,91):
            st*=-square/((2*n)*(2*n+1))
            ct*=-square/((2*n-1)*(2*n))
            new_sine,new_cosine=sine+st,cosine+ct
            if new_sine==sine and new_cosine==cosine:
                return float(sine),float(cosine)
            sine,cosine=new_sine,new_cosine
    raise ValueError("Export trigonometric series did not converge")


def distance(a,b):
    """Keep the serialized residual diagnostic independent of libm as well."""
    with localcontext(DECIMAL_CONTEXT):
        return float(sum((Decimal.from_float(x)-Decimal.from_float(y))**2
                         for x,y in zip(a,b)).sqrt())


def close(a,b,tolerance=MATCH_M):
    return abs(a-b)<=tolerance


def pose(kind,phi,radius,tangent,z):
    s,c=sincos(phi)
    if kind=="barrel":
        return [radius*c-tangent*s,radius*s+tangent*c,z],[[-s,0,c],[c,0,s],[0,1,0]]
    if kind=="endcap":
        return [radius*c-tangent*s,radius*s+tangent*c,z],[[c,-s,0],[s,c,0],[0,0,1]]
    raise ValueError("Unknown chamber orbit kind")


def transform(point,basis,origin):
    return [origin[i]+sum(basis[i][j]*point[j] for j in range(3)) for i in range(3)]


def name(source_id):
    return "MuonChamber_"+re.sub(r"[^A-Za-z0-9_]","_",source_id)


def source_name(pattern,phi,z):
    result=pattern.replace("{phi:02d}",f"{phi:02d}").replace("{z:02d}",f"{z:02d}")
    if "{" in result or "}" in result or not re.fullmatch(r"[A-Za-z0-9_/]+",result):
        raise ValueError("Invalid chamber source-name pattern")
    return result


def centered(panel):
    vertices=panel["vertices_m"]
    offset=[(min(v[i] for v in vertices)+max(v[i] for v in vertices))/2 for i in range(2)]+[0.]
    return [[v[i]-offset[i] for i in range(2)] for v in vertices],offset


def shape_residual(a,b):
    return max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(2))


def factor(panels,system_id):
    """Return 22 source templates, recurrence orbits and exact source manifests."""
    templates=[];entities=[];candidates=[];by_kind=Counter()
    for index,panel in enumerate(sorted(panels,key=lambda p:p["id"]),1):
        vertices,offset=centered(panel)
        family=next((t for t in templates if t["kind"]==panel["kind"] and
                     close(t["depth_m"],panel["depth_m"]) and shape_residual(t["vertices_m"],vertices)<=MATCH_M),None)
        if family is None:
            by_kind[panel["kind"]]+=1
            family=dict(name=("B" if panel["kind"]=="barrel" else "E")+f"{by_kind[panel['kind']]:02d}",
                kind=panel["kind"],vertices_m=vertices,depth_m=panel["depth_m"],representative_source_id=panel["id"],
                members=0,maximum_shape_residual_m=0.)
            templates.append(family)
        family["members"]+=1
        family["maximum_shape_residual_m"]=max(family["maximum_shape_residual_m"],shape_residual(family["vertices_m"],vertices))
        side=0 if panel["kind"]=="barrel" else (1 if panel["origin_m"][2]>0 else -1)
        ids=dict(system=system_id,chamber=index,station=panel["station"],side=side)
        entity=dict(name=name(panel["id"]),source_id=panel["id"],role="chamber",ids=ids,
            origin_m=panel["origin_m"],basis=panel["basis"],vertices_m=panel["vertices_m"],depth_m=panel["depth_m"],kind=panel["kind"],
            template=family["name"],centering_offset_m=offset)
        entities.append(entity)
        q=panel["basis"]
        # The frozen source records the original angle: do not reconstruct it
        # through atan2, whose last bit differs between macOS and Linux libm.
        degrees=panel["compartment"]["phi_deg"]
        angle=degrees if panel["kind"]=="barrel" else sum(degrees)/2
        phi=math.radians(angle%360)
        center=transform(offset,q,panel["origin_m"])
        c,s=(q[0][2],q[1][2]) if panel["kind"]=="barrel" else (q[0][0],q[1][0])
        radius=center[0]*c+center[1]*s;tangent=-center[0]*s+center[1]*c
        token="F" if panel["kind"]=="barrel" else "S"
        match=re.search(r"/"+token+r"(\d{2})(?=/|$)",panel["id"])
        if not match:raise ValueError("Unrecognized source chamber index")
        pattern=panel["id"][:match.start()+2]+"{phi:02d}"+panel["id"][match.end():]
        record=dict(entity=entity,template=family["name"],kind=panel["kind"],station=panel["station"],side=side,
                    radius_m=radius,tangent_m=tangent,z_m=center[2],phi=phi,index=int(match[1]),pattern=pattern)
        theoretical,basis=pose(record["kind"],phi,radius,tangent,center[2])
        if max(abs(basis[i][j]-q[i][j]) for i in range(3) for j in range(3))>MATCH_M:
            raise ValueError("Source basis is not the declared barrel/endcap convention")
        candidates.append(record)
    if dict(by_kind)!={"barrel":15,"endcap":7}:
        raise ValueError("Expected 15 barrel and7 endcap centred shape templates")
    # Collect identical local rows before establishing their actual phi recurrence.
    groups=[]
    for p in candidates:
        group=next((g for g in groups if all(g[0][k]==p[k] for k in ("template","kind","station","side","pattern")) and
                    all(close(g[0][k],p[k]) for k in ("radius_m","tangent_m","z_m"))),None)
        if group is None:groups.append([p])
        else:group.append(p)
    orbits=[];explicit=[]
    for group in groups:
        g=sorted(group,key=lambda p:p["index"]);first=g[0]
        count=len(g)
        index_step=g[1]["index"]-first["index"] if count>1 else 0
        dphi=(g[1]["phi"]-first["phi"])%TAU if count>1 else 0.
        id_step=g[1]["entity"]["ids"]["chamber"]-first["entity"]["ids"]["chamber"] if count>1 else 0
        regular=all(p["index"]==first["index"]+i*index_step and
            p["entity"]["ids"]["chamber"]==first["entity"]["ids"]["chamber"]+i*id_step and
            abs(math.remainder(p["phi"]-first["phi"]-i*dphi,TAU))<=MATCH_M for i,p in enumerate(g))
        if not regular or count<2:
            for p in g:
                e=p["entity"]
                explicit.append(dict(name=e["name"],source_id=e["source_id"],template=e["template"],ids=e["ids"],
                    origin_m=transform(e["centering_offset_m"],e["basis"],e["origin_m"]),basis=e["basis"]))
            continue
        orbit=next((o for o in orbits if all(o[k]==first[k] for k in ("kind","station","side")) and
            o["count"]==count and o["index0"]==first["index"] and o["index_step"]==index_step and
            all(close(o[k],v) for k,v in (("radius_m",first["radius_m"]),("phi0",first["phi"]),("dphi",dphi)))),None)
        if orbit is None:
            orbit={k:first[k] for k in ("kind","station","side","radius_m")}
            orbit.update(phi0=first["phi"],dphi=dphi,count=count,index0=first["index"],index_step=index_step,rows=[])
            orbits.append(orbit)
        orbit["rows"].append(dict(template=first["template"],tangent_m=first["tangent_m"],z0_m=first["z_m"],dz_m=0.,count=1,
            source_pattern=first["pattern"],z_index0=0,z_index_step=0,
            chamber0=first["entity"]["ids"]["chamber"],chamber_phi_step=id_step,chamber_z_step=0))
    # Merge genuine longitudinal recurrences, including ordinary multi-row modules.
    for orbit in orbits:
        groups=[];rows=[]
        for row in orbit["rows"]:
            match=re.search(r"/Z(\d{2})(?=/|$)",row["source_pattern"])
            if not match:rows.append(row);continue
            pattern=row["source_pattern"][:match.start()+2]+"{z:02d}"+row["source_pattern"][match.end():]
            candidate=dict(row,z_index0=int(match[1]),source_pattern=pattern)
            group=next((g for g in groups if all(g[0][k]==candidate[k] for k in ("template","source_pattern","chamber_phi_step")) and close(g[0]["tangent_m"],candidate["tangent_m"])),None)
            if group is None:groups.append([candidate])
            else:group.append(candidate)
        for group in groups:
            g=sorted(group,key=lambda x:x["z_index0"])
            first=g[0]
            if len(g)>1:
                dz=g[1]["z0_m"]-first["z0_m"];step=g[1]["z_index0"]-first["z_index0"]
                idstep=g[1]["chamber0"]-first["chamber0"]
                if all(close(row["z0_m"],first["z0_m"]+i*dz) and row["z_index0"]==first["z_index0"]+i*step and row["chamber0"]==first["chamber0"]+i*idstep for i,row in enumerate(g)):
                    rows.append(dict(first,dz_m=dz,count=len(g),z_index_step=step,chamber_z_step=idstep));continue
            rows.extend(g)
        orbit["rows"]=rows
    model=dict(templates=templates,orbits=orbits,explicit=explicit)
    expanded=expand(model,system_id)
    compare_expansion(expanded,entities,templates)
    return model,entities


def expand(model,system_id):
    """Fail-closed expansion shared by export controls and XML inspection."""
    templates={t["name"]:t for t in model["templates"]}
    if len(templates)!=len(model["templates"]):raise ValueError("Duplicate template name")
    for t in templates.values():
        vertices=t["vertices_m"]
        if not isinstance(t["name"],str) or not re.fullmatch(r"[BE]\d{2}",t["name"]) or t["kind"] not in ("barrel","endcap") or not math.isfinite(t["depth_m"]) or t["depth_m"]<=0:
            raise ValueError("Invalid chamber template identity/depth")
        if len(vertices)!=4 or any(len(v)!=2 or not all(math.isfinite(x) for x in v) for v in vertices):
            raise ValueError("Invalid template vertices")
        for i in range(4):
            a,b,c=vertices[i],vertices[(i+1)%4],vertices[(i+2)%4]
            if (b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])<=0:
                raise ValueError("Template vertices must be convex counterclockwise")
    result=[]
    for orbit in model["orbits"]:
        count=orbit["count"]
        if not isinstance(count,int) or not 1<=count<=936 or not math.isfinite(orbit["phi0"]) or not math.isfinite(orbit["dphi"]) or (count>1 and (orbit["dphi"]<=0 or orbit["index_step"]<=0)):
            raise ValueError("Invalid phi recurrence count/phase/pitch")
        if count>1 and orbit["dphi"]*(count-1)>=TAU-MATCH_M:raise ValueError("Phi recurrence repeats a full revolution")
        if not math.isfinite(orbit["radius_m"]) or orbit["radius_m"]<=0 or orbit["station"] not in (1,2,3) or orbit["side"] not in (-1,0,1):raise ValueError("Invalid chamber orbit")
        if (orbit["kind"]=="barrel")!=(orbit["side"]==0):raise ValueError("Inconsistent kind/side")
        for row in orbit["rows"]:
            if row["template"] not in templates:raise ValueError("Unknown chamber template")
            if templates[row["template"]]["kind"]!=orbit["kind"]:raise ValueError("Template kind mismatch")
            n=row["count"]
            if not isinstance(n,int) or not 1<=n<=936 or n*count>936 or not all(math.isfinite(row[k]) for k in ("tangent_m","z0_m","dz_m")) or (n>1 and (row["dz_m"]<=0 or row["z_index_step"]<=0)):
                raise ValueError("Invalid longitudinal recurrence")
            for iphi in range(count):
                for iz in range(n):
                    identifier=row["chamber0"]+iphi*row["chamber_phi_step"]+iz*row["chamber_z_step"]
                    source=source_name(row["source_pattern"],orbit["index0"]+iphi*orbit["index_step"],row["z_index0"]+iz*row["z_index_step"])
                    origin,basis=pose(orbit["kind"],orbit["phi0"]+iphi*orbit["dphi"],orbit["radius_m"],row["tangent_m"],row["z0_m"]+iz*row["dz_m"])
                    result.append(dict(name=name(source),source_id=source,template=row["template"],origin_m=origin,basis=basis,
                        ids=dict(system=system_id,chamber=identifier,station=orbit["station"],side=orbit["side"])))
    result.extend(model["explicit"])
    if len(result)!=936 or len({e["source_id"] for e in result})!=936 or len({e["ids"]["chamber"] for e in result})!=936 or len({e["name"] for e in result})!=936:
        raise ValueError("Missing/duplicate expanded chamber or source IDs")
    for e in result:
        if e["template"] not in templates:raise ValueError("Unknown explicit chamber template")
        if not 1<=e["ids"]["chamber"]<=936:raise ValueError("Chamber ID out of range")
        q=e["basis"]
        if len(q)!=3 or any(len(row)!=3 or not all(math.isfinite(x) for x in row) for row in q) or len(e["origin_m"])!=3 or not all(math.isfinite(x) for x in e["origin_m"]):
            raise ValueError("Invalid expanded chamber transform")
        if any(abs(sum(q[k][i]*q[k][j] for k in range(3))-(i==j))>MATCH_M for i in range(3) for j in range(3)):
            raise ValueError("Expanded basis is not orthonormal")
        determinant=sum(q[0][i]*(q[1][(i+1)%3]*q[2][(i+2)%3]-q[1][(i+2)%3]*q[2][(i+1)%3]) for i in range(3))
        if abs(determinant-1)>MATCH_M:raise ValueError("Expanded basis is not right handed")
    return sorted(result,key=lambda e:e["ids"]["chamber"])


def compare_expansion(expanded,entities,templates):
    families={t["name"]:t for t in templates}
    if len(expanded)!=len(entities):raise ValueError("Expanded inventory differs from source")
    maximum=0.
    for actual,source in zip(expanded,entities):
        if any(actual[k]!=source[k] for k in ("name","source_id","template","ids")):raise ValueError("Expanded identity differs from source")
        if max(abs(actual["basis"][i][j]-source["basis"][i][j]) for i in range(3) for j in range(3))>MATCH_M:raise ValueError("Expanded source basis mismatch")
        family=families[actual["template"]]
        for xy,source_xy in zip(family["vertices_m"],source["vertices_m"]):
            for sign in (-1,1):
                a=transform([*xy,sign*family["depth_m"]/2],actual["basis"],actual["origin_m"])
                b=transform([*source_xy,sign*source["depth_m"]/2],source["basis"],source["origin_m"])
                residual=distance(a,b);maximum=max(maximum,residual)
                if residual>MATCH_M:raise ValueError("Expanded template vertex differs from source")
    return maximum


def to_xml(parent,model,number,metres):
    container=ET.SubElement(parent,"chamber_templates")
    for t in model["templates"]:
        node=ET.SubElement(container,"chamber_template",name=t["name"],kind=t["kind"],depth=metres(t["depth_m"]),representative_source=t["representative_source_id"])
        for k in (0,3,2,1):ET.SubElement(node,"vertex",x=metres(t["vertices_m"][k][0]),y=metres(t["vertices_m"][k][1]))
    for orbit in model["orbits"]:
        attrs={k:str(orbit[k]) for k in ("kind","station","side","count","index0","index_step")}
        attrs.update(radius=metres(orbit["radius_m"]),phi0=number(orbit["phi0"])+"*rad",dphi=number(orbit["dphi"])+"*rad")
        node=ET.SubElement(parent,"chamber_orbit",**attrs)
        for row in orbit["rows"]:
            attrs={k:str(v) for k,v in row.items() if k not in ("tangent_m","z0_m","dz_m")}
            attrs.update(tangent=metres(row["tangent_m"]),z0=metres(row["z0_m"]),dz=metres(row["dz_m"]))
            ET.SubElement(node,"row",**attrs)
    for e in model["explicit"]:
        attrs=dict(name=e["name"],source_id=e["source_id"],template=e["template"],**{k:str(v) for k,v in e["ids"].items() if k!="system"})
        attrs.update({axis:metres(v) for axis,v in zip("xyz",e["origin_m"])})
        attrs.update({f"a{i}{j}":number(e["basis"][i][j]) for i in range(3) for j in range(3)})
        ET.SubElement(parent,"chamber_placement",**attrs)


def from_xml(detector,system_id):
    def scalar(node,key,unit):
        value=node.get(key)
        if value is None or not value.endswith("*"+unit):raise ValueError("Missing explicit XML unit")
        result=float(value[:-len(unit)-1])
        if not math.isfinite(result):raise ValueError("Nonfinite XML parameter")
        return result
    model=dict(templates=[],orbits=[],explicit=[])
    for node in detector.findall("./chamber_templates/chamber_template"):
        clockwise=[[scalar(v,"x","m"),scalar(v,"y","m")] for v in node.findall("vertex")]
        if len(clockwise)!=4:raise ValueError("Template needs four vertices")
        model["templates"].append(dict(name=node.get("name"),kind=node.get("kind"),depth_m=scalar(node,"depth","m"),vertices_m=[clockwise[i] for i in (0,3,2,1)]))
    for node in detector.findall("chamber_orbit"):
        orbit={k:int(node.get(k)) for k in ("station","side","count","index0","index_step")}
        orbit.update(kind=node.get("kind"),radius_m=scalar(node,"radius","m"),phi0=scalar(node,"phi0","rad"),dphi=scalar(node,"dphi","rad"),rows=[])
        for row in node.findall("row"):
            entry={k:int(row.get(k)) for k in ("count","z_index0","z_index_step","chamber0","chamber_phi_step","chamber_z_step")}
            entry.update(template=row.get("template"),source_pattern=row.get("source_pattern"),tangent_m=scalar(row,"tangent","m"),z0_m=scalar(row,"z0","m"),dz_m=scalar(row,"dz","m"))
            orbit["rows"].append(entry)
        model["orbits"].append(orbit)
    for node in detector.findall("chamber_placement"):
        model["explicit"].append(dict(name=node.get("name"),source_id=node.get("source_id"),template=node.get("template"),ids=dict(system=system_id,**{k:int(node.get(k)) for k in ("station","side","chamber")}),origin_m=[scalar(node,k,"m") for k in "xyz"],basis=[[float(node.get(f"a{i}{j}")) for j in range(3)] for i in range(3)]))
    return model,expand(model,system_id)
