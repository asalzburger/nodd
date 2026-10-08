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
