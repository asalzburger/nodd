# DES-026 — Added solenoid material before ECAL

Date: 2026-10-12. Status: DRAFT / PROTOTYPE estimate.
Human request: estimate the additional pre-calorimeter material in PR64 and
plot t/X₀ against eta. No material inventory or wall design is approved here.

The illustrative reference is **1.40 X₀ at η=0**, with **1.00–2.10 X₀** for
the explicitly varied scenarios. The finite barrel path rises to about
**3.75 X₀ near |η|=1.67** (scenario values2.70–5.63X₀ there). These estimates
are incremental magnet material, including assumed vessel and thermal shield;
they exclude the existing tracker and calorimeter. The range is a scenario
spread, not a confidence interval or an engineered lower/upper bound.

![Added material versus eta](../../design/figures/DES-026-solenoid-material-vs-eta.png)

[Vector plot](../../design/figures/DES-026-solenoid-material-vs-eta.svg),
[summary/assumptions/solid intervals](material.json),
[compressed profile](material-profile.json.gz),
[plot/input hashes](material-figure.json).

## Sourced reference quantities and explicit hypotheses

**FACT — SRC-ATLAS-SOLENOID-2007**, §I/PDF1: the reported45mm cold assembly is
equivalent to0.66X₀. This is the particular ATLAS cold-assembly benchmark; its
shared calorimeter cryostat is not a complete standalone nODD vessel.
**FACT — SRC-PDG-AL-X0-2024**, Aluminum page, radiation-length row:
X₀(Al)=8.897cm. Neither source specifies the nODD bill of materials.

**INFERENCE:** an ATLAS-equivalent cold proxy has an effective length
`45mm/0.66 = 68.182mm per X₀`. Applying this material-per-geometrical-length
proxy to DES026's77.206mm cold annulus gives **1.132X₀ normally**. This assumes
comparable overall occupied-material normalization. It does not claim the
same NbTi/Cu/Al ratios, insulation, reinforcement or load-bearing properties.
The winding/support subdivision remains unresolved; the proxy represents both
once as a whole cold assembly. Do not add a second support slab to it.

**NODD DESIGN CHOICE — illustrative scenarios only**, approving humans:
none recorded; no hardware adoption. Use separate aluminium vessel shells,
annular end closures and a thin thermal enclosure within the reserved volume.
Thicknesses below bracket sensitivity and have no structural qualification.

| Hypothesis | Lean | Reference | Heavier |
| --- | ---: | ---: | ---: |
| Cold proxy across77.206mm | Pure Al surrogate | ATLAS-equivalent | 1.5× ATLAS-equivalent material per length |
| Each inner/outer warm barrel wall | 5mm Al | 10mm Al | 15mm Al |
| Each annular warm end closure | 10mm Al | 20mm Al | 30mm Al |
| Each thermal shell/end wall | 1mm Al | 2mm Al | 3mm Al |

Pure Al is an optimistic composition surrogate, not a real superconducting
winding. The heavier factor1.5 probes additional dense conductor/reinforcement
content; it is not a sourced NbTi recipe. The reference is a planning estimate,
not a best-fit material measurement.

**NODD DESIGN CHOICE — illustrative positions:** warm walls stay at the
DES026 inner/outer vessel radii1.240/1.558656m and end planes±3.850m. Thermal
enclosure limits are r=1.280–1.447m, |z|≤3.650m, placing it around the cold
annulus without intersecting it. These locations are unselected material-model
hypotheses inside the space budget, not a cryogenic engineering design.
The prototype rejects positive-volume overlaps between all material parts;
barrel walls terminate at end-closure inner faces, avoiding joint double counts.
The remaining vessel gaps and81.344mm assembly margin are not filled with metal.

## Ray calculation and interpretation of eta dependence

**INFERENCE — straight geometry rays from the interaction point:**
`r(s)=s/cosh(eta)`, `z(s)=s*tanh(eta)`, with s≥0. Intersect each finite annulus
and axial slab analytically, then sum `path length / effective X₀`. Clip at the
proposed ECAL entrance enclosure r=1.700m or |z|=3.950m; all modeled magnet
parts lie inside it. These entrance planes are not an active-acceptance claim.

This is the usual directional geometric material budget, not a helix-transport
or shower calculation. It is independent of momentum, axisymmetric and
reflection-symmetric, so the figure uses |eta|. Phi-dependent hardware cannot
be described by this single curve.

At central incidence the reference contributions are:

| Incremental modeled component | t/X₀ at eta=0 |
| --- | ---: |
| Whole cold assembly, including winding/support proxy | 1.13235 |
| Two10mm Al warm walls | 0.22479 |
| Two2mm Al thermal shells | 0.04496 |
| **Total** | **1.40211** |

Before finite-end effects, each barrel contribution scales as cosh(eta).
Near |eta|≈1.67, the cold path starts to exit through the coil end before
traversing its full radial width. Above |eta|≈1.72, rays miss the cold annulus.
Warm inner-wall/end-closure material remains somewhat farther forward; above
|eta|≈1.85 rays miss these finite annuli as well. Annular caps and cylindrical
walls have their actual different angular path factors in the toy calculation.
A continued `central thickness × cosh(eta)` beyond the ends would be incorrect.

The apparent forward zero means only that this particular axisymmetric
solenoid inventory is missed. Supports, stiffeners, helium/coolant lines,
chimney, busbars, cables, penetrations and local end-package material are not
inventoried. Calorimeter cryostat, electronics and support material are also
outside this **added-solenoid** estimate. They must be included in the eventual
full pre-calorimeter map; this curve is neither a total material budget nor a
bound on local maxima.

## Reproduction, controls and next decision

```sh
python3 -B tools/solenoid_baseline/material.py
python -B -m unittest discover -s tools/solenoid_baseline -p 'test_*.py' -v
MPLCONFIGDIR=/tmp/nodd-mpl python tools/solenoid_baseline/plot_material.py
```

Executed: Python3.14.6; plotting environment NumPy2.5.3/Matplotlib3.11.2.
Material calculation uses the standard library. No dependency added.
Twelve controls pass: six retained field/energy controls plus six material-ray
controls covering analytic cylinder and endcap path lengths, finite clipping,
misses, cap/wall joint accounting, sign symmetry, scenario ordering, central
component closure and invalid geometry/input rejection. Eta sampling is0.002;
reported peaks are sampled, not engineering precision. Exact configuration,
code/profile and image hashes are retained. PNG/SVG visually checked.

Replace the proxies with a sourced conductor/stabilizer/insulation/mandrel
inventory and qualified wall/shield/support geometry before native DD4hep
material scans or acceptance. Preserve whole-cold-mass material ownership,
include phi-dependent services, and assess tracker+magnet+calorimeter entrance
material together. The larger3T cold assembly and a separate vessel can add
substantial upstream material; estimating its shower impact belongs to the
later performance work requested separately by the user.
