# Proposal for a concise pixel section

- ID: PUB-PIXEL-CONCISE-2026-10-09
- Date: 2026-10-09
- Status: PROPOSED — editorial review
- Source: TDR `279d882179e93b56e522fd6b390c965f6ab18e84`, [current pixel chapter](../tdr/chapters/pixel-detector.tex).
- Purpose: an accurate description of the selected full-simulation model.

I recommend five subsections: **modules and readout**, **barrel layout**,
**endcap layout**, **supports and cooling**, and **services and material
representation**. Keep the sensor/module detail and geometry tables. Shorten
the mounting and cooling prose, combine repeated service descriptions, and
move implementation-sized dimension lists into a compact parameter ledger.
Aim for roughly one third less running text; the final page count should be
checked after typesetting the agreed version.

The synchronized Overleaf chapter remains the authored baseline. The text
below is a proposal held in nODD for review.

## Editing plan

| Current content | Proposed treatment | Information retained |
| --- | --- | --- |
| Sensor/module design, planar sensor and hybrid stack | One subsection; state pitch, channel count and material stack once | Sensor/ASIC thickness, flex composition, active patches, passive guards/seams, local frames and occupied body |
| Longitudinal packing and barrel placement | One subsection and the existing population table | Four radii, stagger, stave/row counts, pitch, inactive intervals and longitudinal phase |
| Endcap stations and ring placement | One subsection, existing station and ring tables | Disc datums, retained rings, local polar axes, alternating faces and sensor depths |
| Stave support; barrel cooling/mounting; disc sandwich; carrier/cooling | One subsection with two short paragraphs and a support/cooling ledger | Material ordering, support thicknesses, tube dimensions, mount locations, carrier envelope and circuit topology |
| Four service extraction subsections | Two paragraphs for barrel/endcap routes, plus a routing ledger | Electrical chain boundaries, cumulative cable loads, coolant branches, collection cells and trunk/rear bounds |
| Material representation | Keep the representation table and a short composition paragraph | Explicit/effective distinctions, constituent conservation, density, packing and the scope of model masses |

The ledger should consolidate the existing numbers, without changing geometry.
It should include the stave layer stack; bearing-ring and foot dimensions;
the disc pickup/stem stack; carrier tongues, rails and flanges; tube diameter
and wall thickness; and local/remote service-cell bounds. Per-chip insert
allocations can be a compact table footnote. Circuit populations belong in the
existing disc inventory table. Flow and temperature assumptions can occupy a
single reference-operating-input row rather than several paragraphs.

## Proposed support and cooling text

**Barrel.** The modules are supported on carbon-foam sandwich staves with CFRP
skins, graphite spreaders and two embedded titanium cooling tubes. The support
lies radially outside the sensitive plane, so an outward-going particle crosses
the sensor before its local stave. The single- and quad-module spines are
10 and 24 mm wide, respectively; the support stack is 4.725 mm deep. Its layer
thicknesses are given in the support ledger. Six CFRP bearing rings per layer
at z = ±110, ±330 and ±546 mm connect the staves to the barrel cage. Each stave
has one foot per ring; the complete barrel contains 24 rings and 492 feet.
The station at z = −546 mm defines the axial datum, while the remaining
contacts permit longitudinal contraction. Two independent evaporative CO₂
circuits run along every stave in opposite directions. Inner/outer stave
tubes have 2.0/2.8 mm outside diameters and 0.11/0.15 mm titanium walls.
At either barrel end, 82 feed and 82 return branches join twelve collection
sectors in the |z| = 555–605 mm service bay.

**Endcap.** Each disc uses a common carbon sandwich annulus from r = 27 to
188.5 mm, including on stations with fewer inner module rings. A 6.0 mm foam
core and two 0.15 mm CFRP skins give a 6.3 mm plate. Modules occupy both faces;
their ASICs face the plate, with per-chip graphite pickups and short stems
providing thermal contact. The two sensor levels on each face are at local
z = ±4.10 and ±5.75 mm. Titanium tubes of 2.8 mm outside diameter and
0.15 mm wall follow the chip rows; azimuthal and radial routes occupy separate
planes at local z = ±1.5 mm. Each row is served by two independent half-ring
circuits. The full pattern has sixteen circuits per disc; the forward
stations have fourteen, twelve or ten according to their retained rings,
giving 248 circuits across both endcaps. Three rim tongues connect each disc
to box rails on a common CFRP carrier. The carrier shell occupies
r = 231.7–232.0 mm over |z| = 609–3136 mm; its rail and flange dimensions
are listed in the support ledger.

One reference-input table can retain barrel/endcap coolant temperatures
−35/−40 °C; inner/outer barrel flow 1.3/2.5 g/s per tube; endcap flow
1.0 g/s per circuit, or 1.1 g/s on the outer quad ring; and the 2.688 W/chip
heat allowance. These are model/design reference inputs. The prose need only
identify evaporative CO₂ and the physical path through ASIC contact, graphite,
support insert and tube.

## Proposed service text

**Barrel.** Electrical services leave each half-stave toward its nearest end.
The central single-chip module is assigned to +z. Serial groups contain at
most sixteen modules and 32 chips, giving two groups per half-stave. Cables
run outside the bearing rings with a 0.5 mm radial clearance and collect in
the same twelve sectors as the coolant branches. The cable envelope grows
with downstream module and group populations. The routing ledger specifies
one data and one command link per module, 1 mm² outer footprint per link,
35 mm² ancillary footprint per group, 75% of a stave pitch for the azimuthal
envelope and 50% cable packing. The sector handoff is at approximately
r = 212 mm, within the r = 190–234 mm service reservation.

**Endcap.** Module tails join ring buses on their own mounting face; three
radial fans per face collect them at the rim. Serial groups stop at half-ring
boundaries and contain at most 32 chips, independently of the coolant circuits.
The full disc has eighteen electrical groups; the forward discs have sixteen,
fourteen or twelve. A 50 mm-deep collector transfers each disc's load to the
axial trunk. The effective trunk material occupies r = 192–231.7 mm in three
90° sectors separated by mounting sectors. The final disc uses an inner
bypass to the rear turn at |z| = 3150 mm; the common rear cell extends to
|z| = 3300 mm and r = 680 mm. Collector positions, local flex dimensions,
the bypass limits and the r = 222 mm flange neck belong in the routing ledger.

## Proposed material summary

Sensor substrates, individual active patches, ASICs, graphite contacts, local
supports, selected mounts and cooling tubes are represented explicitly. Disc
inserts and local service allowances use constituent-normalized volumes;
collectors and remote trunks use effective cells preserving separate cable,
titanium, coolant and void inventories. The representation table identifies
the quantities preserved by each effective component.

Remote cables use provisional volume fractions of 10% copper, 40% polyimide
and 50% air. The additional 50% inter-cable packing allowance is treated
separately. CO₂ inventory uses a reference density of 1.0964 g/cm³.
The pixel assembly model has a mass of 202.753 kg, including 159.383 kg in
downstream transport cells. These are model-inventory masses with the stated
effective compositions and reference coolant density.

## Figures and tables

Retain the overall r–z view, module/stack illustration, barrel layout and first/
last disc view. Pair the stave and disc sections into one support figure;
retain barrel and endcap routing as one figure each; retain the service-cell
interface view. This yields eight principal figure groups, compared with the
current thirteen figure environments. The carrier and sector-handoff sketches
can move to a supporting geometry note; their dimensions stay in the ledgers.
The packing detail can be a small panel of the barrel figure. Existing assets
remain available for technical reference.

Retain the active/sensor dimension table, barrel population, disc station
inventory, ring inventory and explicit/effective material table. Replace
scattered mechanical and service numbers with support/cooling and routing
ledgers. Generated placement tables keep their source snapshot and hashes.

The current track-population assumptions already belong in the overall tracker
coverage section: |η| ≤ 4, pT ≥ 1 GeV, luminous z interval ±150 mm and the
specified field envelope. The pixel layout subsection can refer there once.
This avoids repeating the ring-selection derivation while keeping its domain
of applicability visible.

## Review before applying

Check the proposed text and ledgers against the frozen parameter snapshots;
keep the external technology citations beside the relevant retained claims.
After editorial agreement, apply the changes to the TDR, compile the full
report and pixel extract, and inspect pagination, references and the combined
figures. The current proposal changes presentation only.
