#!/usr/bin/env python3
"""Rebuild DES-010 scale drawings from retained run inputs and verified code."""
from __future__ import annotations
import argparse
from collections import defaultdict
import sys
from pathlib import Path

from services import build,read,write,digest,HERE
from services_geometry import body_envelope
from geometry import _corners

COLOURS={"pixel":"#0072b2","short_strip":"#e69f00","long_strip":"#009e73","shared":"#b66ac1"}


def save(fig,output,name,plt):
    for suffix in ("png","pdf"):
        fig.savefig(output/(name+"."+suffix),dpi=180,bbox_inches="tight")
    plt.close(fig)


def representative_paths(routes):
    """Illustrative axis-aligned paths inside the declared route-tree rectangles.

    At each join use its actual overlap, then connect within the current convex
    rectangle. Small owner-dependent offsets in shared joins keep the three
    paths visible; they do not specify individual cables, bends or packing.
    """
    positive={r["id"]:r for r in routes if r["z_min_mm"]>=0}
    result={}
    for index,sub in enumerate(SUBSYSTEMS):
        current=min((r for r in positive.values() if r["subsystem"]==sub
                     and r.get("regions")==["barrel"]),key=lambda r:r["r_min_mm"])
        point=((current["z_min_mm"]+current["z_max_mm"])/2,current["r_min_mm"])
        points=[point];visited=set()
        while True:
            if current["id"] in visited:
                raise RuntimeError("Illustrative route contains a cycle")
            visited.add(current["id"])
            targets=current.get("connects_to",[])
            following=None
            if not targets:
                if not current.get("exit"):
                    raise RuntimeError("Illustrative route does not reach the conditional handoff")
                destination=(point[0],current["r_max_mm"])
            else:
                if len(targets)!=1:
                    raise RuntimeError("Illustrative route needs one declared downstream connection")
                following=positive[targets[0]]
                z0=max(current["z_min_mm"],following["z_min_mm"])
                z1=min(current["z_max_mm"],following["z_max_mm"])
                r0=max(current["r_min_mm"],following["r_min_mm"])
                r1=min(current["r_max_mm"],following["r_max_mm"])
                if z1<z0 or r1<r0:
                    raise RuntimeError("Illustrative route cannot cross a disconnected join")
                fraction=.3+.2*index if following["subsystem"]=="shared" else .5
                destination=(z0+fraction*(z1-z0),r0+fraction*(r1-r0))
            elbow=(destination[0],point[1]) if current["kind"]=="radial" else (point[0],destination[1])
            for vertex in (point,elbow,destination):
                if not (current["z_min_mm"]<=vertex[0]<=current["z_max_mm"]
                        and current["r_min_mm"]<=vertex[1]<=current["r_max_mm"]):
                    raise RuntimeError("Illustrative centreline leaves its reserved rectangle")
                if vertex!=points[-1]:points.append(vertex)
            point=destination
            if following is None:break
            current=following
        result[sub]=points
    return result


def rz(baseline,modified,routes,envelopes,output,plt):
    from matplotlib.patches import Rectangle,Patch
    fig,axes=plt.subplots(2,1,figsize=(15,10),layout="constrained")
    kept={b["module_id"] for b in modified["bodies"]}
    if envelopes["units"] != "m":
        raise ValueError("Envelope drawing requires explicitly metre-based inputs")
    allocations={region["id"]:region for region in envelopes["regions"]}
    host,vessel=allocations["tracker"],allocations["magnet"]
    host_end=host["z_max_m"]*1000
    vessel_z0,vessel_z1=vessel["z_min_m"]*1000,vessel["z_max_m"]*1000
    vessel_r0,vessel_r1=vessel["r_min_m"]*1000,vessel["r_max_m"]*1000
    positive=[r for r in routes if r["z_min_mm"]>=0]
    plot_zmax=max(vessel_z1,*(r["z_max_mm"] for r in positive))*1.015
    plot_rmax=max(vessel_r1,*(r["r_max_mm"] for r in positive))*1.025
    barrel_turns=[r for r in positive if r["kind"]=="radial" and r.get("regions")==["barrel"]]
    bay_z0=min(r["z_min_mm"] for r in barrel_turns)
    bay_z1=max(r["z_max_mm"] for r in barrel_turns)
    bay_margin=.15*(bay_z1-bay_z0)
    groups=defaultdict(list)
    for b in baseline["bodies"]:
        if b["center_mm"][2]<0 and b["region"]=="endcap":continue
        groups[b["layer_id"],b["row"],b["level"],b["module_id"] in kept].append(body_envelope(b))
    for ax in axes:
        ax.add_patch(Rectangle((vessel_z0,vessel_r0),vessel_z1-vessel_z0,
                               vessel_r1-vessel_r0,facecolor="#6d597a",alpha=.25))
        ax.add_patch(Rectangle((host_end,host["r_min_m"]*1000),
                               max(r["z_max_mm"] for r in positive)-host_end,
                               vessel_r0-host["r_min_m"]*1000,
                               fill=False,edgecolor="#b66ac1",linestyle="--"))
        for key,ee in groups.items():
            r0=min(e["r_min_mm"] for e in ee);r1=max(e["r_max_mm"] for e in ee)
            z0=min(e["z_min_mm"] for e in ee);z1=max(e["z_max_mm"] for e in ee)
            if z1<0:continue
            ax.add_patch(Rectangle((z0,r0),z1-z0,r1-r0,facecolor="#646b73" if key[-1] else "#d1495b",
                                   alpha=.7 if key[-1] else .45,lw=0))
        for s in modified["metadata"]["services"]["supports"]:
            if s["z_max_mm"]<0:continue
            ax.add_patch(Rectangle((s["z_min_mm"],s["r_min_mm"]),s["z_max_mm"]-s["z_min_mm"],
                                   s["r_max_mm"]-s["r_min_mm"],color="#56b4b0",alpha=.7,lw=0))
        for r in routes:
            if r["z_min_mm"]<0:continue
            ax.add_patch(Rectangle((r["z_min_mm"],r["r_min_mm"]),r["z_max_mm"]-r["z_min_mm"],
                                   r["r_max_mm"]-r["r_min_mm"],facecolor=COLOURS[r["subsystem"]],
                                   edgecolor=COLOURS[r["subsystem"]],alpha=.17,lw=.5))
        ax.set(xlabel="z [mm]",ylabel="r [mm]");ax.grid(alpha=.15)
    for sub,points in representative_paths(routes).items():
        axes[0].plot([p[0] for p in points],[p[1] for p in points],
                     color=COLOURS[sub],lw=.9,alpha=.95,zorder=10)
        segments=list(zip(points,points[1:]))
        main=max(segments,key=lambda ab:abs(ab[1][0]-ab[0][0]))
        # One arrow along the main axial trunk and one at the conditional handoff.
        for a,b in (main,segments[-1]):
            start=tuple(x+.46*(y-x) for x,y in zip(a,b))
            end=tuple(x+.56*(y-x) for x,y in zip(a,b))
            axes[0].annotate("",xy=end,xytext=start,
                             arrowprops=dict(arrowstyle="->",color=COLOURS[sub],lw=1),zorder=11)
    axes[0].text(.015,.965,"Illustrative centrelines; finite envelopes govern",
                 transform=axes[0].transAxes,fontsize=8.5,va="top")
    axes[0].set(xlim=(0,plot_zmax),ylim=(0,plot_rmax),title="Positive side; negative side reflected. Filled bands reserve space, not solid material.")
    axes[0].axvline(host_end,color="black",ls=":",lw=1)
    axes[0].annotate("Tracker host ends",xy=(host_end,.025*plot_rmax),xytext=(5,0),
                     textcoords="offset points",rotation=90,fontsize=8)
    axes[0].text(.90*vessel_z1,vessel_r0+.12*(vessel_r1-vessel_r0),"Vessel reservation",fontsize=9)
    shared=[r for r in positive if r["subsystem"]=="shared" and r["kind"]=="radial" and not r.get("exit")]
    if shared:
        rear=max(shared,key=lambda r:r["r_max_mm"])
        axes[0].annotate("New rear collector / bore continuation\nUNAPPROVED interface proposal",
                         xy=((rear["z_min_mm"]+rear["z_max_mm"])/2,
                             (rear["r_min_mm"]+rear["r_max_mm"])/2),
                         xytext=(.67*plot_zmax,.89*plot_rmax),
                         arrowprops=dict(arrowstyle="->",color="#7e4089"),fontsize=9,color="#7e4089")
    axes[1].set(xlim=(max(0,bay_z0-bay_margin),bay_z1+bay_margin),
                ylim=(0,max(r["r_max_mm"] for r in barrel_turns)*1.06),
                title="Barrel escape bays and first endcaps; module positions are unchanged")
    for sub in SUBSYSTEMS:
        turn=max((r for r in barrel_turns if r["subsystem"]==sub),key=lambda r:r["r_max_mm"])
        axpoint=((turn["z_min_mm"]+turn["z_max_mm"])/2,
                 (turn["r_min_mm"]+turn["r_max_mm"])/2)
        axes[1].annotate(sub.replace("_"," ")+" barrel exit",xy=axpoint,
                         xytext=(-85,-35 if sub=="long_strip" else 35),
                         textcoords="offset points",arrowprops=dict(arrowstyle="->",color=COLOURS[sub]),
                         fontsize=9,color=COLOURS[sub])
    handles=[Patch(color="#646b73",label="Retained module bodies"),Patch(color="#d1495b",alpha=.45,label="Removed rows"),
             Patch(color="#56b4b0",label="External support keep-out")]
    handles += [Patch(color=c,alpha=.3,label=s.replace("_"," ")+" services") for s,c in COLOURS.items()]
    fig.legend(handles=handles,loc="outside lower center",ncol=4,fontsize=9)
    fig.suptitle("DES-010 · Tracker routing mockup · PROTOTYPE / working hypothesis",fontsize=15)
    save(fig,output,"routing-rz",plt)


def xy(baseline,modified,routes,output,plt):
    from matplotlib.patches import Wedge,Patch
    from matplotlib.collections import PolyCollection
    from views import convex_hull
    fig,axes=plt.subplots(1,3,figsize=(15,6),layout="constrained")
    kept={b["module_id"] for b in modified["bodies"]}
    for ax,sub in zip(axes,SUBSYSTEMS):
        disc=min((l for l in baseline["layers"] if l["subsystem"]==sub and l["kind"]=="disc" and l["z_m"]>0),key=lambda l:l["z_m"])
        polygons={True:[],False:[]}
        for b in baseline["bodies"]:
            if b["layer_id"]==disc["id"]:
                polygons[b["module_id"] in kept].append(convex_hull([p[:2] for p in _corners(b)]))
        for keep,poly in polygons.items():
            ax.add_collection(PolyCollection(poly,facecolor="#646b73" if keep else "#d1495b",
                                              alpha=.65 if keep else .3,edgecolor="white",lw=.15))
        disc_bodies=[b for b in baseline["bodies"] if b["layer_id"]==disc["id"]]
        disc_extents=[body_envelope(b) for b in disc_bodies]
        disc_z0=min(e["z_min_mm"] for e in disc_extents)
        disc_z1=max(e["z_max_mm"] for e in disc_extents)
        visible_routes=[r for r in routes if r["kind"]=="axial" and r["side"]=="positive"
                        and r["subsystem"] in SUBSYSTEMS
                        and r["z_min_mm"]<=disc_z1 and r["z_max_mm"]>=disc_z0]
        for r in visible_routes:
            ax.add_patch(Wedge((0,0),r["r_max_mm"],0,360,width=r["r_max_mm"]-r["r_min_mm"],
                               facecolor=COLOURS[r["subsystem"]],alpha=.23))
        limit=1.06*max(max(e["r_max_mm"] for e in disc_extents),
                       max((r["r_max_mm"] for r in visible_routes if r["subsystem"]==sub),default=0.))
        ax.set(xlim=(-limit,limit),ylim=(-limit,limit),aspect="equal",xlabel="x [mm]",ylabel="y [mm]",
                                title=f"{sub.replace('_',' ')} at z={disc['z_m']*1000:g} mm\nAll module staggering levels projected")
        ax.grid(alpha=.12)
    fig.suptitle("Reference endcaps and continuous routing annuli · unchanged retained modules",fontsize=14)
    fig.legend(handles=[Patch(color="#646b73",label="Retained body"),Patch(color="#d1495b",alpha=.3,label="Removed full row")]+
               [Patch(color=COLOURS[s],alpha=.3,label=s.replace("_"," ")+" corridor") for s in SUBSYSTEMS],
               loc="outside lower center",ncol=5,fontsize=9)
    save(fig,output,"routing-xy",plt)


SUBSYSTEMS=("pixel","short_strip","long_strip")


def concepts(config,output,plt):
    from matplotlib.patches import Rectangle,FancyArrowPatch
    fig,axes=plt.subplots(1,2,figsize=(13,5),layout="constrained")
    ax=axes[0]
    # Artist coordinates are dimensionless: this panel is explicitly not to scale.
    for x,y in ((0,1.5),(1.1,1.9),(2.2,1.5)):
        ax.add_patch(Rectangle((x,y),.9,.25,color="#646b73"))
        ax.plot([x+.45,x+.45],[1.,y],ls="--",color="#d1495b")
    ax.add_patch(Rectangle((0,0),3.1,1.,facecolor="#56b4b0",alpha=.4))
    ax.plot([.1,3.],[.5,.5],lw=4,color="#009e73")
    ax.text(.1,2.4,"Module / electronics trial bodies",fontsize=10)
    depths=config["support_depths_mm"]
    support_labels="; ".join(f"{s.replace('_',' ')} {depths[s]:g} mm" for s in SUBSYSTEMS)
    ax.text(.1,-.55,"External carrier / cold rail keep-out\n"+support_labels,fontsize=9)
    ax.text(.1,3.25,"Dashed attachments and thermal bridges remain undefined.\nIllustrative staggering; topology sketch, not to scale.",fontsize=9,color="#963747")
    ax.set(xlim=(-.15,3.5),ylim=(-1.1,4.4));ax.axis("off")
    ax.set_title("Local support is separate from the module body")
    ax=axes[1]
    lines=[("LV supply + return / HV / monitoring", "#e69f00"),
           ("Data uplinks + clock / command", "#0072b2"),
           ("Coolant inlet", "#009e73"),("Coolant exhaust", "#6d597a")]
    for i,(label,colour) in enumerate(lines):
        y=4-i
        ax.add_patch(FancyArrowPatch((0,y),(7,y),arrowstyle="<->" if i in (0,1) else "<-" if i==2 else "->",mutation_scale=15,color=colour,lw=2))
        ax.text(.1,y+.15,label,fontsize=10)
    ax.text(0,0,"Local bus / cooling → radial bay → axial annulus\n→ rear collector → conditional vessel interface",fontsize=10)
    ax.text(0,-.8,"Ancillary bundles already include electrical return.\nLocal cooling branches and grouped trunks are distinct.",fontsize=9)
    ax.set(xlim=(-.3,8),ylim=(-1.5,5));ax.axis("off")
    ax.set_title("Routing topology and separate service functions")
    fig.suptitle("Support and services concepts · PROTOTYPE; no engineered stack or material model",fontsize=14)
    save(fig,output,"local-support-concept",plt)


def export(run,output):
    run,output=Path(run),Path(output)
    summary=read(run/"summary.json")
    for name in ("services.py","services_geometry.py","geometry.py","views.py"):
        if digest(HERE/name)!=summary["code_sha256"][name]:raise RuntimeError("Geometry code changed: "+name)
    for name,value in summary["inputs_sha256"].items():
        if digest(run/name)!=value:raise RuntimeError("Retained input hash mismatch: "+name)
    output.mkdir(parents=True,exist_ok=False)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    config=read(run/"config.json")
    baseline,modified,routes=build(config,run/"models.json",run/"layouts.json")
    if modified["metadata"]["services"]["removed_module_ids"]!=summary["services"]["removed_module_ids"]:
        raise RuntimeError("Regenerated removals differ from retained run")
    envelopes=read(run/"envelopes.json")
    rz(baseline,modified,routes,envelopes,output,plt)
    xy(baseline,modified,routes,output,plt)
    concepts(config,output,plt)
    write(output/"views.json",dict(source_commit=summary["source_commit"],run_summary_sha256=digest(run/"summary.json"),
          renderer_sha256=digest(Path(__file__)),input_sha256=summary["inputs_sha256"],
          renderer_command=list(sys.argv),helper_sha256={"views.py":digest(HERE/"views.py")},
          illustrative_paths_zr_mm=representative_paths(routes),
          path_scope="One illustrative barrel-to-handoff path per owner; not cable placement or bend qualification",
          artifacts_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file()}))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--run",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();export(a.run,a.output)
