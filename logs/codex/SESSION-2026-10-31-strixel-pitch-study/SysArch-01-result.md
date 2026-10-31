# SysArch-01 — independent service assessment

Examined1dff0452ed1e7ac24d7b746fccc02ee15df5258d, read-only; model execution and
independent arithmetic, original public PDFs not reread. Source locators come
from the retained DES010 dossier. Explicit role `/root/strixel_services_sysarch`.

8064B/4320EC modules;576B/144EC networks;1584power+fibresets bothends. Gross
cable516.154874L power+37.254217L fibre, collectors/fans and downstreamtransport.
Segmentation-only geometry savings0. Redesign assumption capacities12P0,
networkloads14P+5(B),30P+5(EC), P=P0[(1-f)+f*.5/p]. P0=7.8or31.72881356W.
Forf=.5 allcoarsercases use1/2B/ECbundles, removing242.733803L. Forf=1,
1mm same;1.5/2mm use1/1, removing273.421071L. f=0 removesnone. Data/cooling
fixed. Source13.4mm benchmark has12independentLV+12HVcircuits: require new
conductor/fanout/connector/HV topology, not current-qualified drop-in bundles.

Nativeadditive56pipepairs/end retained. One-end servicearea128902.562506mm²
becomes78133.168587/67979.289803. Worstsector equivalentwidth75.589511mm
becomes46.716592/41.000080mm, atR710,.75azimuth,.5packing. No walls/bends/
connector allowances. Baseline73mm corridor already falls short of worstsector
packing; passing alternative area inequality does not certify installation.

Sources: short_strip_barrel/model.py:145–215,export.py:201–219;
short_strip_endcap/model.py:75–86,121–166,export.py:142–169;
tracker_dd4hep/services.py; DES010 stripdossier SS-F10–12, CMS TDRpp34–35/91.
Copper20% is an effective material fixture, not electrical gauge design.
