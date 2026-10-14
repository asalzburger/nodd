# PR75 - LAr/Si-W barrel-endcap service transition review

2026-10-14. Proposed follow-up, not a design amendment or engineering approval.

Review question: [asalzburger-review on PR75](https://github.com/asalzburger/nodd/pull/75#issuecomment-6163562396)
asks why the ALLEGRO-style LAr barrel/endcap gap is large while Si-W has a small
front seam. The difference is the current nODD service topology, not an intrinsic
800 mm requirement of the calorimeter technology.

## Existing facts and inference

**FACT about current prototype choices:** LAr warm barrel ends at |z|=4.100 m,
and warm endcap starts at 4.900 m. DES032/033 reserve 800 mm for front cryogenic
bends/access and 500 mm behind the endcap. Si-W flange/endcap bounds are
3.920/3.950 m; its 30 mm front seam is installation-only. DES034 places a
300 mm external backbone outside both Si-W package corner radii and a 400 mm
rear break in HCAL for radial exit. The ECAL front gap is not its service budget.

**INFERENCE reproducing the selected LAr arithmetic:** services.json chooses
80 mm nitrogen and 100 mm LAr utility jackets, a bend radius of 4xOD, 20 mm
installation clearance and a radial move from R=2735.3 to 3029 mm. For the
100 mm jacket, radial shift 293.7 mm and bend radius 400 mm give
`2R*sin(acos(1-shift/(2R))) + 20 + 100 = 739.403 mm`.
The 800 mm allocation adds about 60.6 mm to that assumed S-bend envelope. It
is not a demonstrated minimum or complete installed route. For Si-W's chosen
50 mm water jacket, a single 200 mm-radius quarter turn plus half-jacket and
20 mm clearance needs 245 mm inside the 400 mm rear break. These are different
pipe/topology hypotheses, not comparable proofs of a technology advantage.

**FACT / limitation:** LAr services.py uses the N2 branch radius for both
80 mm N2 and 100 mm LAr utility-line S-bend examples. Actual utility-specific
feedthrough origins, wall penetrations, ports, headers and connection shapes
are undefined. Physical cryostats require suitable penetrations and connections;
that does not select their location or mandate this front-gap size. Si-W likewise
has no connected cassette-collector/port network. Its endcap corners lie inside
the barrel's circumscribed radius, allowing its selected annulus to continue
beside both. LAr's warm endcap radius (2.949 m) exceeds the warm barrel radius
(2.830 m), and the selected N2 origin lies farther inward; the chosen route shifts
outward before passing the endcap.

The gap contributes to LAr's unresolved partial-depth barrel/endcap transition.
No quantified performance improvement is claimed by reducing it.

## Proposed bounded follow-up

1. Define end-to-end service exits for LAr fill/drain/vent/relief, N2 supply/return,
   electrical/data/HV and tools/access, with actual cryostat port positions, jacket
   sizes, bend rules, connector footprints and support/thermal ownership. Do the
   analogous collector-to-backbone closure for Si-W; compare the same completeness.
2. Compare the current front S-bend route with barrel-side ports feeding the outer
   annulus and rear radial egress. Determine the minimum usable front gap from
   explicit routes and installation sequence. Any smaller gap is a prototype
   design amendment, not a number selected solely to improve the RZ drawing.
3. After a route option is chosen, check cryostat/support/cable/pipe containment,
   revise ECAL/HCAL and collar/FCal interfaces, and map material and full-depth
   sensitive crossings versus eta/phi. Update the candidate page and matched
   reviewer overview/PDF. Response validation follows separately.

Keep the current envelopes until that study establishes a viable alternative.
No geometry, detector package, source evidence, approval or external dependency
changes in this review response.

## Pinned primary records

- [LAr choices and bend derivation, DES032](https://github.com/asalzburger/nodd/blob/48e97256f8badd75c022a84ab1c4ff71977c56a2/docs/design/DES-032-allegro-lar-barrel.md#service-packing-and-amended-hcal-interface)
- [LAr service parameters](https://github.com/asalzburger/nodd/blob/48e97256f8badd75c022a84ab1c4ff71977c56a2/tools/lar_calorimeter/services.json)
- [LAr bend arithmetic](https://github.com/asalzburger/nodd/blob/48e97256f8badd75c022a84ab1c4ff71977c56a2/tools/lar_calorimeter/services.py)
- [LAr endcap/transition, DES033](https://github.com/asalzburger/nodd/blob/72d37ee9a56182e4ba974791a848a738c19cf092/docs/design/DES-033-allegro-lar-endcaps.md#forward-and-transition-geometry-interpretation)
- [Si-W service topology, DES034](https://github.com/asalzburger/nodd/blob/0a26796518d690bf26934d2864d63ecad7582675/docs/design/DES-034-siw-service-envelopes.md#external-backbone-and-hcal-interfaces)
