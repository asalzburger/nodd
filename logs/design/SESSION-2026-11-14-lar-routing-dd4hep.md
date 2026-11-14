# SESSION-2026-11-14-lar-routing-dd4hep — native service routing prototype

## Scope and selected requests

User requested a DD4hep version of the routing, allowing bend approximation while
keeping material. On explicit clarification selected existing steel/N2 pipe
materials and retained cable envelopes. New isolated implementation branch/worktree
starts at3fca74b70709345a9440b17cf23acb40aab1f945, stacked on the existing proposal
branch; production geometry and sign-off states remain unchanged.

Read governing AGENTS/PROJECT/design docs. Using nodd-coordinate/design-evidence/
review-validation and acts-spack. Preflight reported changed setup/lock fingerprints;
warned before dependency use and verified current DD4hep/DDG4 imports, ROOT6.40.04,
Geant411.4.3 and installed datasets. Fresh software/env/run.sh activation used;
sandbox sysctl/ps warnings did not prevent successful runtime checks. Fingerprints
are captured in ignored build/lar-routing/environment-observation.json. No shared
installation or source download changed.

Initial design input records the user-selected material boundary, common-endpoint
mass matching, proposed mitered CutTube approximation and separate native versus
integrated-fit gates. No guessed cable/jacket material is introduced.

## Contracts recorded before dispatch

Explicit generic role fallback, not native profile loading. Source ownership is disjoint; only SoftEng writes code, coordinator owns records.

```json
[
  {
    "input_revision": "b0d54812e668714c14a3193e57ed4365f2fcbd01",
    "inputs": [
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/design/inputs/DES-032-side-rear-routing.md",
      "tools/lar_calorimeter/barrel_geometry.py",
      "tools/lar_calorimeter/barrel_services.py",
      "tools/lar_calorimeter/services.json",
      "prototypes/calorimeter/LArBarrel.cpp",
      "prototypes/calorimeter/CMakeLists.txt",
      "software/env/run.sh"
    ],
    "completion": "Return assignment ID, exact input/source versions, conclusions and actual checks/failures/limits. No native engineering acceptance or nested delegation. Do not commit or push; coordinator owns Git/publication.",
    "id": "LAR-ROUTING-SoftEng",
    "role": "SoftEng",
    "mode": "write",
    "writable_paths": [
      "prototypes/lar_routing/CMakeLists.txt",
      "prototypes/lar_routing/LArRouting.cpp",
      "tools/lar_calorimeter/routing.py",
      "tools/lar_calorimeter/routing_config.json",
      "tools/lar_calorimeter/routing_native.py",
      "tools/lar_calorimeter/routing_transport.py",
      "tools/lar_calorimeter/test_routing.py"
    ],
    "task": "Implement the isolated DD4hep routing component and reproducible exporter/native checks per the new design input. User explicitly selected existing20mm-OD18mm-ID steel/N2 construction; cable/jacket envelopes stay unmaterialised metadata, never fake material. Common start |z|3000 R2735.3 and downstreamhand-off4800 produce same4968.343720697463mm analytic path forold/new; preserve both constituent volumes via sqrt(Lanalytic/Lpoly) scaling ofradii at unchanged density/recipe. Prefer mitered CutTube pieces; installed DD4hep Shapes.h confirms CutTube(rmin,rmax,dz,startPhi,endPhi,lx,ly,lz,tx,ty,tz). Exact join normals/proper transforms, 5degree default arcstep, guard degeneracy, XMLunits explicit. Build a standalone factory (no production CMake change), source-bound expected inventory, native count/recipe/mass/overlap/joint-navigation audit and small Geant4conversion/transport smoke. Use scoped meaningful tests, resolution/negative controls. May write ignored build outputs under build/lar-routing/softeng only. Node preflight has changedsetup/lock warnings already shown; currentROOT6.40.04, DD4hep/DDG4 imports, Geant411.4.3/datasets verified by coordinator in fresh software/env/run.sh. Read acts-spack instructions before native use; never install/concretize. Report integration contacts rather than cutting existing calo material. Root owns docs/inventory/tracking/logs; propose interface improvements via message.",
    "deliverable": "Return bounded implementation/assessment to coordinator; tracked source only within owned paths, actual native evidence ignored if generated."
  },
  {
    "input_revision": "b0d54812e668714c14a3193e57ed4365f2fcbd01",
    "inputs": [
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/design/inputs/DES-032-side-rear-routing.md",
      "tools/lar_calorimeter/barrel_geometry.py",
      "tools/lar_calorimeter/barrel_services.py",
      "tools/lar_calorimeter/services.json",
      "prototypes/calorimeter/LArBarrel.cpp",
      "prototypes/calorimeter/CMakeLists.txt",
      "software/env/run.sh"
    ],
    "completion": "Return assignment ID, exact input/source versions, conclusions and actual checks/failures/limits. No native engineering acceptance or nested delegation. Do not commit or push; coordinator owns Git/publication.",
    "id": "LAR-ROUTING-SysArch",
    "role": "SysArch",
    "mode": "read-only",
    "writable_paths": [],
    "task": "Assess the physical interface boundary of this material-preserving standalone route prototype. Check matched path scope/counts, known20mm cooling-pipe recipe versus100mm emptyjacket, source/header ambiguity, closedwall/board/ring contacts and whether any full-context composition can be called valid. Recommend bounded integration diagnostics without silently cutting/removing existingcalorimeter material. No native runtime needed; no artifact writes.",
    "deliverable": "Return bounded implementation/assessment to coordinator; tracked source only within owned paths, actual native evidence ignored if generated."
  },
  {
    "input_revision": "b0d54812e668714c14a3193e57ed4365f2fcbd01",
    "inputs": [
      "docs/design/inputs/DES-032-routing-dd4hep.md",
      "docs/design/inputs/DES-032-side-rear-routing.md",
      "tools/lar_calorimeter/barrel_geometry.py",
      "tools/lar_calorimeter/barrel_services.py",
      "tools/lar_calorimeter/services.json",
      "prototypes/calorimeter/LArBarrel.cpp",
      "prototypes/calorimeter/CMakeLists.txt",
      "software/env/run.sh"
    ],
    "completion": "Return assignment ID, exact input/source versions, conclusions and actual checks/failures/limits. No native engineering acceptance or nested delegation. Do not commit or push; coordinator owns Git/publication.",
    "id": "LAR-ROUTING-PhysVal",
    "role": "PhysVal",
    "mode": "read-only",
    "writable_paths": [],
    "task": "Assess the scientific/material preservation method before implementation. Independently derive common-endpoint old/new analytic path equality, constituent referencevolumes and radius correction for chordal mitered CutTubes. Check preservation ofcomposition/density versusV/mass/X0 and limits for directional material budget and exactcircularshape, joins/overlaps/resolution guards. User selected existingpipe materials and cableenvelopes; do not infer fullservicebill or physical100mm jacket. Recommend discriminating native/G4 validation, no native runtime or artifact writes needed.",
    "deliverable": "Return bounded implementation/assessment to coordinator; tracked source only within owned paths, actual native evidence ignored if generated."
  }
]
```

## Implementation handoff and candidate cycle

SoftEng completed seven owned files;55LAr controls including16routing tests pass.
Initial native/G4 evidence verifies2752pieces,5376jointpoints/2688crossings,
zero10nm overlaps and three saved native geantino events pervariant with aimed
miters. Retained adverse diagnostics: initial ROOTteardown failure (explicit
Detector.destroyInstance/MTcleanup fixed); no-HC passive ROOT has noeventframes
(actualstepJSONL is evidence); G4gun roundspositionUI (only fixturevertices are
explicitly quantized, strict observed-input check retained). Existing sources
are frozen for a clean candidate build/export/validation cycle.

Root identified direct use of existing nlohmann-json3.12.0 /uecyhyo; made its
CMake target dependency explicit and registered this preinstalled header-only
package in the inventory. No dependency installed. Prior v3 receipts correctly
reject the CMake-only source-binding change; they are diagnostics, not the final
executed candidate. Task record state spelling was corrected to existingactive.

Independent SysArch and PhysVal initial contributions atb0d54812 confirm matched
path/material arithmetic and construction conditions, but explicitly reject any
claim of integrated fit. Full native context sampling already witnesses duplicate
upstream pipes and closed walls, with actualpipe versusemptyenvelope diagnostics
kept separate. Final source-bound results and exact-revision review follow.
