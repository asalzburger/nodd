# LAYOUT-002 — Tracker + inner3T solenoid + ALLEGRO-style LAr ECAL

**User-requested alternative, DRAFT / PROTOTYPE.** LAYOUT-001 remains the
separate SiW candidate. This layout retains the tracker and conditional inner
magnet, replaces both EM calorimeter parts, and enlarges HCAL/service envelopes.

[![LAYOUT-002 R–Z envelopes and empty forward insertion](figures/LAYOUT-002-rz.png)](figures/LAYOUT-002-rz.svg)

| Component | Concise features | Status / decisions |
| --- | --- | --- |
| Tracker | Gen3 barrel/endcaps;45,646 recorded sensitive planes | On main; [DES025](../design/DES-025-tracker-dd4hep-gen3.md) |
| Inner solenoid | Central3T target; existing inner-coil allocation retained | Conditional open [PR64](https://github.com/asalzburger/nodd/pull/64); enlarged HCAL needs a new complete field solution |
| LAr EM barrel | SamplingR2.1728–2.5783m;1536 inclined Pb/steel/PCB periods,11 compartments;2.286M cells | [PR73](https://github.com/asalzburger/nodd/pull/73), [DES032](../design/DES-032-allegro-lar-barrel.md); outer cryostatR2.830m, half-length4.100m |
| LAr EM endcaps | Three tilted turbine wheels,R0.410–2.790m;450mm sampling at|z|5.010–5.460m;601,600cells/end | [PR74](https://github.com/asalzburger/nodd/pull/74), stacked after PR73; [DES033](../design/DES-033-allegro-lar-endcaps.md); packageR0.301–2.949m,|z|4.900–5.860m |
| Cold services | Barrel5888 board slots/96 cooling half-branches; each endcap1584 slots/48 branches | Explicit PCB/package/spreader/N2 proxies; no qualified headers, feedthroughs or thermal contact |
| External services |300mm radial barrel corridor;181mm neck beside endcaps;800mm front/500mm rear gaps | Empty bend/cable/pipe reservations; [budget](../validation/DES-032/services.json), [inputs](../../tools/lar_calorimeter/services.json) |
| HCAL | Steel/scintillator outline; front apothem3.130m, outer4.6259m, barrelhalf5.860m; ends6.360–7.8559m | Envelope only; retain1.4959m total depth; detailed mass/support/field follow-up |
| Forward EM / FCal | LAr does not cover|eta|4; hatched collar/FCal spaces remain empty | Dedicated insertion deferred; [ADR009](../decisions/ADR-009-layout002-lar-calorimeter.md) |
| Muon system / magnets | Absent | Future work |

The native barrel and both endcaps have material/readout/overlap evidence,
including saved-hit sparse transport checks; see [DES032 results](../validation/DES-032/results.md)
and [DES033 results](../validation/DES-033/results.md). This overview combines
those ECAL envelopes with recorded tracker and conditional magnet bounds;
it is not a constructed full detector.

The endcap's annular full-depth envelope is approximately1.424<|eta|<3.198.
Wheel support strips and turbine faces still change active paths. Partial-depth
barrel/endcap transition and forward response need further design. The future
FCal box is not acceptance. The258kW adverse planning power exceeds the200kW
cooling reference; extra space is not thermal/hydraulic qualification.

[Drawing inputs and pinned source revisions](LAYOUT-002.json) ·
[Vector view](figures/LAYOUT-002-rz.svg) ·
[Alternative SiW candidate](LAYOUT-001-tracker-3t-siw.md) ·
[All layouts](README.md).
