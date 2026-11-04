# SESSION-2026-10-13-calorimeter-wedge-correction

## Selected human request and correction

The human expected “B — Proposed carrier approach” to be augmented with edge
sensors while remaining producible as wedges. The earlier four-quadrant
optimization changed that architecture without making the choice clear.
The correction retains sixteen22.5-degree wedges; the previously authorized
eta4 prototype target still applies. No engineering sign-off is inferred.

## Outcome and provenance

Restored B's compact centred rows,2mm PCB margins/gaps,5mm tangential side
allowance plus1mm half-seam,30mm supported inner rim and120mm peripheral
shared-service bay. Individual sensor boards are the first implemented member
of B's full/half/single family; grouping/routing remains open. A100mm-apothem
16-gon aperture keeps the supported corner at132.55mm, below the eta4 front
radius144.742mm. These are unsigned nODD choices derived from the B drawing and
the human's prototype target, not manufacturer/machine-qualified dimensions.

Each wedge/layer has76 intact squares and36 custom inner/side masks (29 oriented
profiles;14 small/narrow remainders rejected). Squares and IDs survive edge
addition unchanged. All masks/PCBs remain inside one wedge. The sector ID field
now has4 bits; superseded quadrant IDs are not a compatible baseline. The new
full-face fractions are59.98%/69.47%; the custom gain is9.48 percentage points.
At eta4,64.44% of360 sampled azimuths cross at least40/48 active layers;
zero-hit seams remain. Custom inner masks supply forward reach that squares
cannot provide within these narrow wedges.

Generated and visually inspected the four-stage SVG and a dedicated single-wedge
before/after SVG with an inner-sensor detail. Archived previous quadrant
figures, catalogue and native/transport evidence rather than relabeling them.
DES030/ADR008, tools/README and project tracking now describe wedge production.
No HCAL/barrel/production entry point or new external software changed.
Existing public partial-sensor/compact-board precedents remain architectural
sources; new physical/process/support parameters are nODD choices.

## Actual checks and limitations

The acts-spack preflight returned2 for setup/lock fingerprint drift. Warned the
human and reverified existing DD4hep1.38/7deaacd, ROOT6.40.04 and Geant4
11.4.2/cpge6jj runtime/imports/configured data. No shared installation modified.
The unchanged compiled standalone C++ factory/segmentation was reused.

Both complete48-layer ECAL native audits pass all parts/materials/replicas,
volume-ID and logical-electrode/raw-fragment/boundary checks, with zero ROOT
overlaps at1e-5mm. Final native rays cover wedge centres and both sides of a
physical seam: eta4 centre probes cross48 layers with custom masks; seam probes
cross0. Squares cross0 at eta4. Source and final expected-inventory hashes
were checked before copying evidence. Runs identify parent69b044e plus exact
working-source hashes, not a future merge revision.

Two sparse single-layer custom inner trapezoid Geant4 fixtures,10GeV mu-,
field0,FTFP_BERT,seeds43/44, save expected positive-energy hits on both ends
(module5,pad[-3,3]). Final fixture hash matches these completed events.
Full-detector transport, electrical/charge response, machine aperture,
mechanics/thermal/hydraulic engineering and grouped-board routing remain open.
All22 hardware controls,28 project/document controls and record validators pass.
One documentation patch context mismatch made no edits and was corrected.
The journal validator also rejected a manual inspection marked PASS without
a shell exit code; moved that evidence to tool activity and reran validation.
The final code/source correction is1593bc5e25b8b297c348aa43559d88606bf87968,
pushed on codex/calorimeter-edge-sensors and delivered by existing draft PR70,
stacked on PR69. PR title/description were rewritten around the final wedges.
Hosted CI refresh was pending at this journal snapshot; its completion is
reported separately in the user-facing delivery.

## Token accounting

No exact current client counters were exposed. Usage is empty/unknown, never
zero or estimated. Prior209 disjoint observations/620812827 observed tokens
remain unchanged. Validator accepted176 paired session records.
