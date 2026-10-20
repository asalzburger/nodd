# PR90 chamber refinement

User requests addressing additional PR90 comments6286557527 and6286566047. Start clean 5f42c4b9649619771e8d5ec70247c99b10d8e80f. New human direction permits inner gap filler chamber type and middle whole-sector simplification. Keep unsigned isolated PROTOTYPE, magnets/barrels/frame fixed. Existing scientific evidence preserved; no engineering sign-off. Exact per-turn root/child usage unavailable, not zero.

## CR-M1 before dispatch

```json
{
  "id": "CR-M1",
  "role": "MuonTech",
  "input_revision": "5f42c4b9649619771e8d5ec70247c99b10d8e80f",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_layout/wheels.py",
    "tools/muon_layout/wheels-config.json",
    "tools/muon_layout/geometry.py",
    "docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json",
    "docs/validation/DES-040/inner-closure-2026-10-20/README.md"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/refined_wheels.py",
    "tools/muon_layout/refined-wheels-config.json",
    "tools/muon_layout/test_refined_wheels.py"
  ],
  "task": "Implement new isolated PROTOTYPE followup to human PR90 comments6286566047 and6286557527. Latest explicit human requirements: (0) inner fan gaps need closure using another chamber type, respecting real fixed BT slots; (1) middle wheel can use3 chamber dimension families: one full sector type plus two chamber types for coil-containing sector; (2) all3 apertures cover |eta|<3 and need not extend farther forward. Keep magnets, frame, barrel panels, station z/depth/outer radius bounds unchanged unless physical impossibility reported. Current middle216panels bothends; simplify whole-sector cassette outlines. Existing g.prism supports convexquads only: prefer convex quadrilateral/trapezoid fillings to limit native/export complexity. Do NOT silently invent filled annular cryostats or move magnets. Need concrete whole-volume-safe gap closure geometry and three-family middle recipe; primary source inspection first. New DES040 preimplementation amendment will be written by root before source work. You own only3newfiles; do not modify existing physics/data, root owns documents,exports, runtime, all generated outputs. Public new output dir will be docs/validation/DES-040/refined-wheels-2026-10-20/candidate; return API build(baseline,config) or sensible clear function + CLI --geometry/--config/--output with source identities and exact transform/dimension counts. Provide actual geometric certificates against coils, all484supports+allotherchambers/pairs, finite eta3 aperture convention (nearest face, avoid unintended overcoverage); consult SysArch child independently if helpful via root. Human instruction permits added type and whole-sector middle simplification but does not grant engineering qualification. Record cassette size exemptions explicitly; output remainsunsigned. Focus meaningful positive/negative tests. No nestedagents, dependencies, sharedACTS edits, Git commits or externalmessages. Read saved complete fallback prompt and skills first.",
  "deliverable": "3ownednewsource/config/test files implementing deterministic revised wheel outlines with bounded fullvolume geometry checks and reproducible report to root.",
  "completion": "Inneravoidablegapsclosedexceptrequiredslots/seams, middleexact3dimensionfamilies if feasible, eta3apertures correct and adversecontrols fail; report limitation promptly."
}
```

## CR-A1 before dispatch

```json
{
  "id": "CR-A1",
  "role": "SysArch",
  "input_revision": "5f42c4b9649619771e8d5ec70247c99b10d8e80f",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_layout/wheels.py",
    "tools/muon_layout/wheels-config.json",
    "tools/muon_layout/geometry.py",
    "docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json",
    "docs/validation/DES-040/inner-closure-2026-10-20/README.md",
    "tools/muon_layout/support.py",
    "tools/toroid_prototype/geometry.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independent fixed-interface and aperture/spacing study for latest PR90 comments6286557527/6286566047. Human asks innergapclosure additionaltype, middle3shapes (fullsector1 vscoilsector2), aperturescover|eta|<3/no more needed. Sourceactualcurrentgeometry/magnet/coils/frame. Quantify front/backfacesandBT/ECT positions; isinner/middlebefore/within toroids? Explain movingmiddleoutsidewouldchange leverarm/field traversal and requiredz/rearframe envelope; do notassumearea=>momentumgain. Derive feasible middle3shape recipe using actual BT/ECT phi phases andwarm+50mmclearance andsupportprisms; rootsMuonTech implementsseparately. Derive conservative finite-depth eta3 aperture respectingglobalphi and radial versus apothem; nominate nearestface/centralplane convention, give all3innerapertures and quantify smallpolygon excess. Need independently check newshapes whenready, but now sourcefeasibility input. Preservefixedmagnets/frame/z/depth/outerbounds. Concrete geometricwitnesses, not qualitative assertions. Scratchonly /private/tmp/pr90-CR-A1-*, portable checker --repo/--revision/--output asneeded. No repository/dependency/source edits, nestedagents, Git commits or externalmessages.",
  "deliverable": "Sourcepinned SysArch inputs on geometry/eta/spacings, clear constraints, feasible3shape construction or actual obstruction, portable evidence/report.",
  "completion": "Root can implement requested refinement and answer moving-wheel question with quantitative geometric/leverarm limits. No approval claim."
}
```


## Reconciliation before implementation

CR-M1 proposes three inner families: twelve core trapezoids plus pre/post-slot seam-centred filler trapezoids, retaining real BT slots and small measured local guard wedges. Three middle families replace the old 108/end with 36/end; outer24/end retained with revised aperture. All quadrilateral volumes use the existing native engine. Root recorded explicit30mm bore half-gap, normal20mmseams, cassette outline exceptions and nominal eta3 convention before source work. Root review caught a half-width versus full seam offset in the first filler draft; writer corrects actual physical normal separation to20mm and adds adverse controls before freeze.

CR-A1 independently confirms positions and fixed physical obstacles. Inner6.4956–6.9956 is before ECT7.05–11.95 but within BT; middle9.25–9.75 is inside both; outer12.55–13.05 is beyond them. Three-family middle packing necessarily opens its bores beyond the nominal eta3 target because the fixed ECT inner legs occupy that region. At the middle nearface the complete eta3 circle lies within the union of actual warm ECT legs; neither chamber topology nor an aperture label removes material. A narrow middle z~10.9 shift also fails the normal three-trapezoid aperture bounds; moving beyond all toroids conflicts with rearframe and outerwheel spacing. Preserve stations and report limitation; no silent magnet/field change.

Root prepares new native/export/XY/crossing wrappers with all dated inputs unchanged. Spack warning and unavailable optional Python acts binding are recorded; fresh-shell native C++ runtime and exact existing engine/writer/core fingerprints pass. No rebuild or dependency mutation was needed.

## Source freeze

CR-M1 author reports six meaningful tests passed and final source frozen. All192 new endcaps receive fresh analytic coil/support proof plus independent adaptive warm-sweep audits (343392cells). All778128 chamber-pair broadphases pass. Root's half-seam finding was corrected: physical filler/core normal gap is20mm. Weak49mmclearance/19mmseam, badstation/support, occupiedBT, incorrectrotatedbound, nominaleta3withoutECTguard, occupiedsupport andduplicatepanel controls reject. Three/three/one families and72/72/48endcapcounts bothends;1248total with1056unchangedbarrels. Local remainingguardarea.535996800447m²/end is explicit. MiddleFULL/BT_LOWbores1.01/1.066512492 yieldsectorcentreetalimits2.910787733/2.856683758.

CR-A1 portable independent sourcepinned contribution retained in review/interface-*; its conservative1.07BTbore illustration is distinct fromfinalgenerator. Bothnominalapertureconventions are named; chosenvalueu0=Rnear andphysicaleta3obstruction are explicit. No source/dependency changes byreader. Root freezes newgenerator/config/tests and native artifact/crossing wrappers before final acquisition.
