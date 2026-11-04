"""Plot the categorized Geant4 material scan with unrooted.

Run in the pinned software/analysis unrooted environment.
Input JSON is exported and independently verified by export_profiles.py.
The component profile means are additive because EVERY geantino (including
zero contribution) is filled in EVERY component. Their errors are correlated;
the uncertainty band is obtained from the total per-track profile instead of
adding component variances.
"""
import argparse
from pathlib import Path
from importlib.metadata import distribution, version
import csv
import hashlib
import json
import os

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--data", type=Path, required=True, help="Exported profiles.json")
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
DATA = json.loads(args.data.read_text())
OUT = args.output.resolve()
OUT.mkdir(parents=True, exist_ok=True)
os.environ["MPLBACKEND"] = "Agg"
os.environ["MPLCONFIGDIR"] = str(OUT / ".mpl-cache")
os.environ["XDG_CACHE_HOME"] = str(OUT / ".cache")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb, to_hex
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
from unrooted.core import Axis, Histogram
from unrooted.plot import HistogramStyle
from unrooted.plot.mpl import stack, plot
from unrooted.plot.plotly import stack as interactive_stack, plot as interactive_plot
from plotly.subplots import make_subplots


SUBDETECTORS = ["beam_pipe", "pixel", "short_strip", "long_strip"]
DISPLAY = ["Beam pipe", "Pixel", "Short strip", "Long strip"]
COLORS = ["#697681", "#2171b5", "#e58b20", "#37815b"]
COMPONENTS = [f"{d}_{s}" for d in SUBDETECTORS for s in ("nonsensitive", "sensitive")]
ACTIVE = [0, 2, 3, 4, 5, 6, 7]
LABELS = [f"{DISPLAY[i//2]} · {'sensitive' if i%2 else 'non-sensitive'}" for i in range(8)]
AXES = {"eta": (r"Pseudorapidity $\eta$", "Pseudorapidity η", 0.1),
        "abs_eta": (r"Absolute pseudorapidity $|\eta|$", "Absolute pseudorapidity |η|", 0.1),
        "phi": (r"Azimuth $\phi$ [rad]", "Azimuth φ [rad]", np.pi/36)}
YLABELS = {"X0": (r"Mean material $\langle t/X_0\rangle$", "Mean material ⟨t/X₀⟩"),
           "L0": (r"Mean material $\langle t/\lambda_{\mathrm{I}}\rangle$", "Mean material ⟨t/λᵢ⟩")}
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":11,
                    "axes.titlesize":12, "axes.labelsize":12,
                    "axes.spines.top":False,"axes.spines.right":False,
                    "axes.edgecolor":"#a3abb3", "grid.color":"#dfe4e8",
                    "grid.linewidth":0.65, "hatch.linewidth":0.5,
                    "savefig.facecolor":"white"})

def style(i):
    color = COLORS[i//2]
    if not i%2:
        rgb=np.asarray(to_rgb(color))
        color=to_hex(.62*rgb+.38)
    return HistogramStyle.as_stack(line_color=color, fill_color=color,
             fill_alpha=1.0, line_width=.45, fill_hatch="/" if i%2 else None)

STYLES = [style(i) for i in range(8)]
def contribution(hist):
    # The profile spread does not stack; the means have a common denominator.
    return Histogram(axes=[Axis(hist.axes[0].edges.copy())],
                     values=hist.values.copy(), variances=hist.variances.copy(),
                     name=hist.name)

def fetch(axis, quantity):
    group=DATA["axes"][axis]
    def hist(name):
        values=group["quantities"][quantity][name]
        return Histogram(axes=[Axis(np.asarray(group["edges"]))],
                         values=np.asarray(values["mean"]), variances=np.asarray(values["variance"]), name=name)
    histograms=[hist(c) for c in COMPONENTS]
    total=hist("total")
    np.testing.assert_allclose(sum(h.values for h in histograms),total.values,rtol=2e-13,atol=2e-14)
    return [contribution(h) for h in histograms], contribution(total)

def finish_ax(ax, axis, quantity):
    ax.set_xlabel(AXES[axis][0]); ax.set_ylabel(YLABELS[quantity][0])
    ax.set_xlim((-4.5,4.5) if axis=="eta" else ((0,4.5) if axis=="abs_eta" else (-np.pi,np.pi)))
    ax.set_ylim(bottom=0); ax.grid(axis="y"); ax.set_axisbelow(True)
    ax.margins(y=.07)
    if axis=="phi":
        ax.set_xticks([-np.pi,-np.pi/2,0,np.pi/2,np.pi],
                      [r"$-\pi$",r"$-\pi/2$","0",r"$\pi/2$",r"$\pi$"])

def contrast_hatches(ax):
    for patch in ax.patches:
        if patch.get_hatch():
            patch.set_edgecolor("#243747")

def save(fig, stem):
    for extension in ("png","pdf","svg"):
        target=OUT/f"{stem}.{extension}"
        fig.savefig(target,dpi=180,bbox_inches="tight")
        if extension=="svg":
            target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines())+"\n")
    plt.close(fig)

report=DATA["classification"]
assert report["unassigned_steps"]==0
assert report["density_mismatches"]==0
ntracks=report["tracks"]
counts={axis:np.asarray(DATA["axes"][axis]["counts"]) for axis in AXES}
checks={"tracks":ntracks,"steps":report["steps"],
        "source_profile_data_sha256":hashlib.sha256(args.data.read_bytes()).hexdigest(),
        "plot_script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "classification":report,
        "independent_ROOT_checks":DATA["checks"],
        "sensitivity_allocation_bound":DATA["sensitivity_allocation_bound"],
        "minimum_tracks_per_bin":{a:int(n.min()) for a,n in counts.items()}}
for axis in AXES:
    assert counts[axis].sum()==ntracks
    assert np.all(counts[axis]>0)
    assert np.all(counts[axis]==np.floor(counts[axis]))
    for quantity in ("X0","L0"):
        histograms,total=fetch(axis,quantity)
        edges=total.axes[0].edges
        with (OUT/f"profiles_{axis}_{quantity}.csv").open("w",newline="") as stream:
            writer=csv.writer(stream,lineterminator="\n")
            writer.writerow(["bin_low","bin_high","tracks","total_mean","total_sem"]+
                            [f"{c}_mean" for c in COMPONENTS]+[f"{c}_sem" for c in COMPONENTS])
            for b in range(len(total.values)):
                writer.writerow([edges[b],edges[b+1],counts[axis][b],total.values[b],total.errors[b]]+
                                [h.values[b] for h in histograms]+[h.errors[b] for h in histograms])

total_style=HistogramStyle.as_line(line_color="#202c37",line_width=1.0,
                 error_display="band",error_color="#202c37",error_alpha=.2)
for axis in AXES:
    fig,axes=plt.subplots(2,1,figsize=(12.7,8.5),sharex=True)
    fig.subplots_adjust(left=.09,right=.72,bottom=.10,top=.85,hspace=.09)
    fig.suptitle("nODD tracker material budget",x=.09,y=.965,ha="left",fontsize=20,weight="bold",color="#233747")
    fig.text(.09,.919,f"Geant4 geantino scan  ·  {ntracks:,} tracks  ·  mean per geantino",fontsize=11.5,color="#52606b")
    fig.text(.09,.888,"Barrel and both endcaps combined; all tracks contribute to every component mean.",fontsize=10,color="#52606b")
    interactive=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=.09)
    for row,(quantity,ax) in enumerate(zip(("X0","L0"),axes),1):
        histograms,total=fetch(axis,quantity)
        stack([histograms[i] for i in ACTIVE],ax=ax,styles=[STYLES[i] for i in ACTIVE],uncertainty=False)
        contrast_hatches(ax)
        plot(total,ax=ax,style=total_style)
        finish_ax(ax,axis,quantity)
        if row==1: ax.set_xlabel("")
        part=interactive_stack([histograms[i] for i in ACTIVE],labels=[LABELS[i] for i in ACTIVE],
                               styles=[STYLES[i] for i in ACTIVE],uncertainty=False)
        for trace in part.data:
            if row==2: trace.showlegend=False
            interactive.add_trace(trace,row=row,col=1)
        for trace in interactive_plot(total,style=total_style,label="Total ± statistical SEM").data:
            trace.showlegend=False
            interactive.add_trace(trace,row=row,col=1)
        interactive.update_yaxes(title_text=YLABELS[quantity][1],rangemode="tozero",row=row,col=1)
    handles=[Patch(facecolor=STYLES[i].fill_color,edgecolor="#243747" if i%2 else STYLES[i].line_color,
                   hatch=STYLES[i].fill_hatch,label=LABELS[i]) for i in ACTIVE]
    handles.append(Line2D([0],[0],color="#202c37",label="Total ± statistical SEM"))
    fig.legend(handles=handles,loc="upper left",bbox_to_anchor=(.735,.853),frameon=False,
               fontsize=10.3,labelspacing=1.3,handlelength=1.9,title="Material contributions",title_fontsize=11)
    fig.text(.75,.265,"Beam pipe has no\nsensitive component.",fontsize=10,color="#52606b",linespacing=1.5)
    fig.text(.09,.028,"Sensitive = DD4hep sensitive-volume flag. Passive silicon (ASICs, guards and seams) stays non-sensitive.",
             fontsize=9,color="#52606b")
    save(fig,f"material_budget_{axis}")
    interactive.update_layout(template="plotly_white",width=1150,height=800,
        title=dict(text=f"nODD tracker material budget<br><sup>Geant4 · {ntracks:,} geantinos · mean per geantino · active sensor volumes hatched</sup>"),
        margin=dict(t=105,b=70,r=250),legend=dict(x=1.02,y=1,itemclick=False,itemdoubleclick=False),
        hovermode="x unified")
    interactive.update_xaxes(title_text=AXES[axis][1],row=2,col=1)
    interactive.write_html(OUT/f"material_budget_{axis}.html",include_plotlyjs=True)

# Per-subdetector panels make the sensitive fraction visible on a local scale.
fig,axes=plt.subplots(4,2,figsize=(13,12.5),sharex=True)
fig.subplots_adjust(left=.09,right=.97,bottom=.085,top=.89,hspace=.30,wspace=.24)
fig.suptitle("Material budget by subdetector",x=.09,y=.967,ha="left",fontsize=20,weight="bold",color="#233747")
fig.text(.09,.931,f"Geant4 · {ntracks:,} geantinos · Δ η = 0.10 · means include tracks with no crossing",color="#52606b")
for row,display in enumerate(DISPLAY):
    for col,quantity in enumerate(("X0","L0")):
        histograms,_=fetch("eta",quantity)
        selected=[2*row,2*row+1]
        if row==0: selected=[0]
        ax=axes[row,col]
        stack([histograms[i] for i in selected],ax=ax,styles=[STYLES[i] for i in selected],uncertainty=False)
        contrast_hatches(ax)
        finish_ax(ax,"eta",quantity)
        ax.set_title(display,loc="left",weight="bold")
        if row<3: ax.set_xlabel("")
        ax.tick_params(labelsize=10)
fig.legend(handles=[Patch(facecolor="#bcc8d1",label="Non-sensitive"),
                    Patch(facecolor="#557b99",edgecolor="#243747",hatch="/",label="Sensitive")],
           loc="upper right",bbox_to_anchor=(.97,.973),ncol=2,frameon=False)
fig.text(.09,.025,"Sensitive flags are taken from the geometry, including active pixel patches; silicon alone does not imply sensitivity.",
         fontsize=9.5,color="#52606b")
save(fig,"material_budget_subdetectors_eta")

checks["unrooted_version"]=version("unrooted")
checks["unrooted_source"]=json.loads(distribution("unrooted").read_text("direct_url.json"))
checks["validation"]= ["curated bin counts sum to the full scan", "material density match at every step (native classification)",
   "all steps assigned", "per-track sum matches recorded totals within float32 accumulation precision",
   "every component includes zero-contribution tracks", "profile sums match total means",
   "native TProfile means and variances independently checked by export_profiles.py", "no axis underflow/overflow",
   "all eta, |eta| and phi bins populated"]
checks["artifacts"]=[{"name":p.name,"bytes":p.stat().st_size,
    "sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(OUT.glob("material_budget_*"))]
(OUT/"validation.json").write_text(json.dumps(checks,indent=2)+"\n")
print(json.dumps({"status":"PASS","tracks":ntracks,"steps":report["steps"],"artifacts":len(checks["artifacts"]),
                  "minimum_tracks_per_bin":checks["minimum_tracks_per_bin"]},indent=2))
