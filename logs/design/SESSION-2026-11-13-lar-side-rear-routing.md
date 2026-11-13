# SESSION-2026-11-13-lar-side-rear-routing — Concrete LAr side-neck and rear-egress routing proposal

## Scope and selected request

Exact user request: “Can you make a suggestion for 1) ?” The referenced option
is side/rear service egress in the earlier gap assessment. This refines existing
draft PR142 on its dedicated branch; it is not an independent publication or
geometry-implementation task. The new bounded follow-up has its own paired
session. Initial source e5e1ecd68bbdcd8c3f9e6402e2089db1c8eab751 was clean.
PROJECT stageB authorization applies; no sign-off state is advanced.

The assistant proposes barrel-side necks before the end face, a straight R3029mm
outer bus and rear outward turns, preserving initial pipe/bend/station/channel
hypotheses. The one-metre abs(z)3000–4000mm neck band is a drawing target, not an
empty volume or demonstrated fit. The100mm line's739.403mm offset envelope can
be screened there only after actual header/port, board and support design.

## Outcome and limitations

The routing note supplies topology, dimensional reservations, ownership handoffs
and gates before a smaller front gap. The ideal rear turn needs490mm including
both axial-face clearances, leaving10mm of500. Straight100mm bus clearance is
30mm to ECAL and51mm to HCAL. Existing planning capacity has only28 spare board
slots; a side neck cannot silently remove populated rows. No manifold/flow
consolidation is assumed. The endcap rear support remains unported.

A possible400mm inward endcap study would create900mm between its back and HCAL
endcap. The coordinator caught and corrected the distinction that the HCAL barrel
still blocks outward exit before5860mm: the full radial window remains500mm.
Additional rear space can house headers inside the annulus; widening the radial
turn requires an HCAL/interface amendment. The prospective collar also blocks
an unchanged inward translation. No new geometry or performance result is claimed.

## Separate SysArch contribution

LAR-SIDE-REAR-SysArch, explicitly assigned to reused thread
01a1d3d3-37d1-7271-a9fb-9642616f74a4, /root/larplace_physval. The prepared generic
prompt included the role mandate; native profile loading is not claimed.
Examined e5e1ecd68bbdcd8c3f9e6402e2089db1c8eab751. Independently checked pinned
inputs, bend/clearance/capacity calculations and closed barrel-shell construction.
Recommended the pre-end S-bend neck instead of an impossible470mm elbow in
300/181mm corridors; agreed with490mm two-face rear screen and fixed500mm
full radial-exit window. Proposed R4800mm as a provisional handoff beyond HCAL's
4716.5mm corners, subject to magnet/yoke allocation. No writes or native jobs.
This is a separate baseline-interface contribution, not an independent review
of the final authored note or human engineering acceptance.

## Commands, checks and sources

- Inspected governing docs and source parameters; new shell commands used the
  existing checkout and standard-library Python only. No ACTS/DD4hep/Geant4 use
  or dependency installation.
- Recalculated S-bend, sampled circular swept-elbow axial extrema,28-slot planning
  margin and fixed500mm HCAL exit. Checked Markdown table column counts.
- Project records and software inventory pass; no software/dependency integration
  changed, so no inventory prose change was needed.
- Actual ATLAS Canada historical feedthrough page inspected and catalogued only
  as sealed cold/warm/vacuum-interface precedent. CDS cryogenics PDF challenged;
  its search snippet was not adopted as a fact. No source PDF downloaded.
- Existing e5e1ecd PR142 CI verified green: build14m33s, analysis3m41s,
  token-site39s. New documentation-head CI is separate and not claimed complete.

## Token accounting

Usage-only recovery selects the completed SysArch turn for this session:
886,519input+15,036output=901,555total tokens;861,568cached input and11,855reasoning
output are included subsets. Current coordinator finalized counters unavailable
and excluded. The newly available prior coordinator8,542,399tokens were imported
into their original assessment owner, not duplicated here. Models/provider/version
remain unreported. Raw archives/private model state were not retained.

## Assignment recorded before dispatch

Explicit generic SysArch fallback; role/profile instructions included in prepared prompt.

```json
{
  "id": "LAR-SIDE-REAR-SysArch",
  "role": "SysArch",
  "input_revision": "e5e1ecd68bbdcd8c3f9e6402e2089db1c8eab751",
  "inputs": [
    "docs/design/DES-032-allegro-lar-barrel.md",
    "docs/design/DES-033-allegro-lar-endcaps.md",
    "docs/design/inputs/DES-032-transition-review.md",
    "docs/design/inputs/DES-032-hadron-gap-options.md",
    "tools/lar_calorimeter/services.json",
    "tools/lar_calorimeter/services.py",
    "tools/lar_calorimeter/barrel_services.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Develop/critique one concrete topology to remove the front cryogenic S-bend: barrel outer-side feedthrough/neck to an axial bus outside the endcap, then radial egress in the rear service break; endcap services on rear. Preserve current OD/bend assumptions initially. Check the 100mm utility quarter-turn470mm against300mm barrel and181mm endcap corridors; do not call that elbow a fit. Consider a localized barrel-side service box/neck allowing the existing S-bend to occur along the barrel rear periphery before z4100, or a tangential/3D alternative. Identify rings/boards/closed shells, field/HCAL/forward and rear-support obstructions and explicit endpoint handoffs. Recommend the most defensible first prototype, numbers that are screening targets only, and missing requirements. No geometry modification, native runtime or nested delegation.",
  "deliverable": "Return cited concrete preferred route, initial dimensions/envelopes, governing failure checks and alternatives. Coordinator curates into a PR142 follow-up design input.",
  "completion": "Name exact input revision and locators, actual checks, limitations and no file changes. Do not infer engineering acceptance or a validated reduced gap."
}
```
