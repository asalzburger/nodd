# Author seed-length diagnostic provenance

DRAFT geometry-only diagnostic by BO-M1, using the same final `barrel_overlap.py` source as freeze `7d8c51f304dc79bd187279580b4e1cb5464f7974`. These are author diagnostics, separate from the final native/central-bank validation. Source SHA256: `e57597636d2634bd93f8cd38e00a1ca63500d7ebaff85751288e9a86471899ac`.

[Actual diagnostic output](seed-diagnostics.json) contains the 3 m and 6 m maximum-seed alternatives. Each invokes `build` with the pinned refined baseline and final configuration, overriding only `max_barrel_length_m`. That runs fresh packing, certified z-seam merging, pair/interface checks and uncached coil audits. No hardware or clearance changes are selected. The 4 m candidate was selected provisionally; this is not an engineering optimum.

The shared bank has 16,384 independent directions, fixed seed 40090, **signed** cos(theta) uniform between `-tanh(1)` and `+tanh(1)`, full phi. It is not mirrored. At each station, both depth faces must fit inside one cassette; union across cassettes then require all three barrel stations. Borders 0/0.03 m use the same bank. There is no coil/support ray veto, material, endcap or transport calculation. This differs intentionally from the final 32,768-iid mirrored bank at seed 906320.

Executed API/observable reproduction, from the repository root with Python and NumPy (no native libraries):

```python
import copy, json, numpy as np
from tools.muon_layout import barrel_overlap as b, geometry as g
c = json.loads(b.DEFAULT_CONFIG.read_text())
base = json.loads((b.ROOT / c['base_geometry']).read_text())
rng = np.random.default_rng(40090)
n = 16384
mu = rng.uniform(-np.tanh(1), np.tanh(1), n)
phi = rng.uniform(0, 2*np.pi, n)
d = np.column_stack((np.sqrt(1-mu**2)*np.cos(phi),
                     np.sqrt(1-mu**2)*np.sin(phi), mu))
result = {}
for length in (3., 6.):
    config = copy.deepcopy(c)
    config['max_barrel_length_m'] = length
    geo, ct = b.build(base, config)
    out = {}
    for border in (0, .03):
        hits = np.zeros((n, 3), bool)
        for p in geo['panels']:
            if p['kind'] == 'barrel':
                ix = np.flatnonzero(~hits[:, p['station']-1])
                hits[ix, p['station']-1] |= np.isfinite(
                    g.midplane_hits(p, d[ix], border, True))
        out[str(border)] = dict(station_fractions=hits.mean(axis=0).tolist(),
            three_station_fraction=float(hits.all(axis=1).mean()))
    result[str(length)] = dict(counts=ct['counts'],
        size_report=ct['dimensions_after'], packing=ct['max_z_seam_merging'],
        quick_geometry=out)
print(json.dumps(result, indent=2))
```

The author executed this calculation and saved the JSON in scratch, which the coordinator copied without changing values. The example omits only scratch geometry/control saves and progress printing. The 3 m alternative yields 816 barrels and 13 families, three-station 59.8206% / border 51.5015%; the 6 m alternative 672 barrels and 14 families,67.0105% / 60.1440%. The selected 4 m author diagnostic was 69.5435% / 62.201%; final separately acquired central-bank fractions are reported in the main README. Small differences between those banks are not geometry changes.
