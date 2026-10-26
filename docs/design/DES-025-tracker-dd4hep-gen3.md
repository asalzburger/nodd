# DES-025 — BeamPipe + Tracker assembly and ACTS Gen3 conversion

- Status: DRAFT
- Date: 2026-10-08
- Scope: explicitly user-authorized integration for software review; no design sign-off.

Assemble DES024 pipe, DES019 trimmed mixed pixel, selected phi-tilted DES020
short-strip barrel, DES021 endcap and DES022/023 paired long strips. Keep all
sensor placements, signed local axes, bounds, disc datums and readout IDs unchanged.
No field or upstream ODD material map is introduced. Existing coverage, guard,
warm thermal, sag/joint and service-capacity qualifications remain limited.

NODD DESIGN CHOICES: one deterministic compact assembled from independently
exported inputs; shared natural elements and Air/Vacuum, otherwise namespaced
materials preserve each source recipe exactly. World half sizes take component
maxima; truth region encloses all sensors. The passive pipe reserves system0;
pixel systems1–3 retain their IDs. Standalone strips systems3–6 translate
losslessly to assembly systems4–7 to avoid the discovered system3 collision;
all other placement fields and all bit layouts are unchanged. Shared service corridors need one
physical carrier and a conserved constituent inventory; duplicated standalone
trunks must be reconciled explicitly and recorded, never silently overlapped.

ACTS Gen3 uses the native DD4hep backend and DD4hep-backed sensitive elements,
not a separately regenerated layout. Group actual sensitive DetElements by
system/layer placement IDs, retaining every pixel chip and both strip faces.
XYZ sensor axes follow local Box coordinates in these factories. ROOT centimetres
convert to ACTS millimetres. Group barrel and signed-z disc layers into radial
subsystem containers with connected Gen3 portals. Navigation envelopes are
software margins, not extra detector material or a physical clearance claim.

The pipe is represented by a thin cylindrical material surface at the wall
mid-radius27.4 mm, thickness0.8 mm, with native Be properties and finite half
length4000 mm. This is the usual tracking approximation to the physical shell;
DD4hep retains both exact wall boundaries. Sensor material can be native silicon;
passive tracker services require a dedicated material mapping campaign, no ODD
map is silently substituted. A correct geometry alone does not qualify material
mapping, alignment, field propagation or reconstruction performance.

Validate native construction, identifiers, per-source sensor centres/axes/bounds,
material preservation, cross-component overlaps, pipe clearance, Geant4 transport,
one ACTS surface per native sensitive element, cylindrical pipe material and
Gen3 navigation through all subsystems. Retain failure evidence and exact source,
input, factory and installed ACTS hashes; enclosing result commits are distinct.

The retained DES023 exporter already describes cumulative barrel+endcap service
loads. Its shared corridor replaces the DES022 standalone barrel trunk; keeping
both would double-count the same barrel payload. Short-strip standalone trunks
share identical radii/azimuths: partition at all source axial boundaries, sum
constituent payload volumes, retain one aluminium carrier, and count unused air
once. These integration ownership choices do not claim that fixed service
packing limits pass. Export fails on inconsistent carrier materials, excess
physical inventory or non-conserved payload. Source models/artifacts stay intact.

## Beam-pipe clearance amendment for review

The first combined audit found pipe/support and pipe/service intersections:
the old passive pixel apertures began at27mm, inside the27.8mm outer wall.
As a NODD DESIGN CHOICE within this user-authorized integration, the combined
compact opens only passive pixel annuli to28.8mm (1mm radial clearance). The
optional clarification was left open while independent software checks and the
explicit candidate were completed; this tested convention is the review proposal.
No maintainer sign-off is inferred. Original standalone producers/pins and their
retained artifacts remain unchanged. All sensor transforms, guard dimensions,
IDs and disc datums remain exact. The outer service radii remain fixed.

For homogenized core/skin plates retain non-filler cooling/spreader inventory
and subtract only foam/CFRP from the enlarged hole. For service cells retain all
non-air conductor, coolant and pipe volumes, remove unused air and renormalize
density/mass fractions to the new cell volume. Pure skins lose only the clipped
annulus. The candidate removes10.1283g across138 passive parts; no silicon loss.
No mechanical stiffness, vacuum support or service-packing pass is inferred.
`--keep-pixel-aperture` retains the unamended historical control, which must fail
clearance validation with the new pipe.

The centralized assembly truth region is r<1200mm, |z|<3600mm, a software
enclosure of all native sensitive nodes (not an acceptance specification).
World bounds use maxima of the standalone envelopes. Current1mm navigation
envelopes and the physical1mm pipe clearance are separate design choices.


## Configurable Gen3 portal material-mapping trial (2026-10-26)

Status: **PROTOTYPE / DRAFT**, explicitly requested by the human in PR100's
local task. These are NODD DESIGN CHOICES for an isolated mapping campaign;
no engineering sign-off or production acceptance is recorded.

Select one physical portal for each native sensitive layer: the outer cylinder
for pixel barrels (material after the sensitive layer), and the inner cylinder
or upstream signed-z disc for all other sensitive layers. Additional carriers
are the beam pipe, inner/outer cylinders at each pixel–short-strip and
short–long-strip gap, two barrel/endcap separator discs per subdetector,
and the outer tracker cylinder plus both outer shell discs. Deduplicate
shared physical portals while retaining all logical roles. The existing
geometry has52 signed sensitive layers; this literal scheme is expected to
have about65 unique carriers, rather than forcing the approximate50 target
by dropping layers. The selection manifest records the actual count.

All counts are configurable. Initial phi bins=1. The other axis is z for
cylinders and r for discs:

| Carrier | z/r bins |
| --- | ---: |
| Pixel barrel; short-strip barrel | 250 |
| Long-strip barrel | 100 |
| Beam pipe; full gap cylinders | 500 |
| Pixel endcap; pixel barrel/endcap separators | 50 |
| Short-strip endcap; short-strip barrel/endcap separators | 100 |
| Long-strip endcap; long-strip barrel/endcap separators | 50 |
| Full outer shell discs | 250 |
| Full outer shell cylinder | 500 (explicit full-cylinder default) |

The side selection above specifies carrier placement relative to the native
sensitive layer. Use the pinned ACTS mapping/validation algorithms and disclose
their actual material-assignment rule. The current upstream assignment code
uses closest intersected surfaces; a MappingType field alone does not impose
strict per-step before/after assignment.

Map the complete recorded material inventory, including silicon and the pipe,
onto these selected portals. Clear existing native material slabs in the
mapping/validation geometry before assigning ProtoSurfaceMaterial or loading
the map, so no sensor or pipe material is counted twice. DD4hep solids, physical
materials and sensor transforms remain unchanged. Keep the native-slab survey
geometry as a separate control. No ODD material map is introduced.

Read the existing100k recording, run native mapping, serialize/reload the map,
then run validation with an explicit independent random seed and the same
eta/phi support. Overlay the validation total X0/lambdaI profile on the existing
Geant4 component stack. Retain empty bins, missed surfaces, unmapped material,
profile differences and all source/input/runtime identities. A visually close
curve is not a material-order, tracking-performance or design acceptance claim.


The native outer pixel-barrel cylinder is a merged full-length portal shared
with the inner pixel–short-strip gap cylinder. It requests250 z bins as a layer
and500 as a full gap. The configurable `maximum_requested` shared-portal policy
uses500 on this one physical portal and retains both requested roles in the
manifest;an `error` policy or explicit per-portal override is also available.
Current selection is66 logical roles on65 physical portals (15 cylinders,
50 discs),8550 nominal bins. No duplicate material map is installed on the
shared boundary. Native shell choice is the existing World exterior:its
outer cylinder and two end discs;the separator discs are the native barrel-end
portals. These exact choices and counts are an implementation of this trial,
not a new physical envelope.

## Cumulative material diagnostic requested in PR100 expert review

The [2026-10-26 expert comment](https://github.com/asalzburger/nodd/pull/100#issuecomment-6415806657)
requests mean accumulated X₀/λI versus barrel radius, forward |z| and flight
distance d=√(r²+z²), comparing the existing Geant4 recording with ACTS validation.
This is a diagnostic of the isolated prototype, with no detector change.

NODD DESIGN CHOICES for display: |η| intervals of width 0.5 over 0…4.5;
radius for |η|<0.5, |z| for |η|≥1.5, and d for every interval. Sampling grids
initially extend to 1200/4200/4500 mm with 2/5/5 mm spacing respectively;
all choices are configurable and carry no accuracy acceptance criterion.

For origin straight rays, integrate the recorded Geant4 step budget uniformly
between its physical pre/post coordinates, clipping partial steps at each
coordinate threshold. Keep mapped validation material as a thin interaction
at its recorded portal position. Compute cumulative values per ray first,
then the slice mean and population SEM over every ray, including zeros.
Preserve material totals at the final threshold; show separate sample counts
and source hashes. Finite checkpoint spacing limits the displayed localization.
These curves diagnose longitudinal/radial shifts and do not establish material
order relative to every sensor, curved-track performance or design acceptance.
