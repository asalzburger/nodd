# SESSION-2026-10-20-fcal-3d-svg — LAYOUT-001 FCAL illustration

## Scope and request

The user requested a 3D SVG of the tungsten/quartz FCAL for LAYOUT-001 and no more than ten sentences explaining the technology choice and main features. This bounded continuation started at `165d297ac6f45c37cb8e996f26a6115c119cf7de` on `codex/common-fcal-design`, with a clean working tree. PR88 remained open, ready for review; that state was preserved and does not confer design approval.

## Delivered result

Created a self-contained, editable orthographic SVG cutaway, a rendered PNG preview and an eight-sentence plain-text explanation. The reproducible standard-library generator reads the existing input and finite model. Its metadata retains input/model/generator hashes, dimensions, exact counts and display omissions. Camera, colours, removed quadrant, sparse enlarged fibres and wireframe rear enclosure are display choices only. No design parameters, numerical reports, native model or production files changed.

The full module is 1800 mm long with physical radii 50/290 mm, a 1200 mm sampling block, 300 mm fan-out and the existing readout/cooling/service intervals. The main view shows 74 real lattice sites as enlarged representative fibres; the inset shows all 96 cartridge footprints. The eight caption sentences distinguish long/short depth weightings from independent compartments and retain the prototype qualification limits. Tiny clamshell joints, ribs and detailed services are omitted in the illustration. Machine clearance, radiation lifetime, optical/shower response and engineering qualification remain open.

DES039 and the LAYOUT-001 page link the artifacts. The existing FCAL task lists the new deliverables and journal evidence; no lifecycle or human-sign-off state was advanced. This small dependent illustration remained with the coordinator; no fresh separate scientific review is claimed.

## Provenance and actual checks

Read the existing DES039/ADR010, technology dossier, inputs, finite model, native sensor/coldplate placements and layout page. Rechecked the existing primary PDG tungsten table (density and interaction/radiation lengths) and CMS HF paper (abstract and section 2: Cherenkov fibres, radiation motivation and rear extraction). Their existing source IDs are `SRC-PDG-TUNGSTEN-2025` and `SRC-CMS-HF-WEDGES-2008`; no new normative source or design choice was introduced. CASTOR experimental HTML was inaccessible; no claim relies on that retrieval.

Generated SVG, parsed XML, checked source hash/dimensions/counts, verified the projection basis is orthonormal and confirmed no scripts or embedded raster. The complete SVG is vector. Rendered with rsvg-convert 2.62.3 and visually inspected; moved two leaders/labels to remove crossings and pinned the SiPM leader to an actual cartridge. An initial multi-file patch failed exact-context matching and made no changes; corrected the patch and regenerated. No failed scientific test was discarded.

`draw_3d.py --check` passed; all 11 existing FCAL controls passed in 1.831 seconds; the retained physics report check passed unchanged; project records validated 67 tasks, 38 documents and 21 review rounds. The paired JSON records the exact observed command results. No native runtime or shared installation was used or modified for this illustration.

## Token accounting and revision

Exact client per-turn counters are unavailable, so usage remains empty and this task's input/output totals remain unknown. The journal summary validated 185 records; historical observed usage is not allocated to this task. The paired JSON inventory covers all new and modified files. Git history identifies the enclosing commit without a self-reference.

Final journal validation passed all 185 records, the token-site build succeeded and project-record validation passed again. These record checks grant no detector approval.
