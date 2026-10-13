# LAYOUT-001 — Tracker + inner 3 T solenoid + Si–W ECAL

**Current human-selected candidate · DRAFT / PROTOTYPE · updated 2026-10-13.**
The tracker is maintained on main. Open component proposals are included in this
candidate for review; combined detector construction and engineering sign-off
remain pending.

![Candidate R–Z view](figures/LAYOUT-001-rz.png)

| System | Main features | Decisions and PRs |
| --- | --- | --- |
| Tracker | RD53i mixed single/quad pixels; short and long strips; Be pipe. 45,646 sensitive planes. | [DES025](../design/DES-025-tracker-dd4hep-gen3.md), [pixel choice ADR007](../decisions/ADR-007-itkpix-pixel-baseline.md), [PR58 — merged](https://github.com/asalzburger/nodd/pull/58) |
| Solenoid | Inside ECAL; central 3 T target. 7.2 m cold length; 7.7 m vessel allocation; 1.64 m outer reservation. | [DES026](https://github.com/asalzburger/nodd/blob/4e44d7c650ac0a2931f7fc1637b5b3f2dfbe4c95/docs/design/DES-026-tracker-solenoid-baseline.md), [sizing direction PR6](https://github.com/asalzburger/nodd/pull/6#issuecomment-5809476152), [PR64 — open](https://github.com/asalzburger/nodd/pull/64) |
| EM calorimeter | Si–W, 48 layers; barrel square-board slabs, inner apothem 1.70 m. Endcaps at ±3.95 m: sixteen wedge carriers with custom edge sensors; η = 4 exploration target. | [Barrel DES031](https://github.com/asalzburger/nodd/blob/19d20f843e0ccebf4fb34dffcf51a89ce1e8e62a/docs/design/DES-031-siw-barrel-prototype.md), [Endcap DES030](https://github.com/asalzburger/nodd/blob/5664d16aea2df36222dc0099ba18594cf506304d/docs/design/DES-030-ecal-edge-sensors.md), [aperture/carriers ADR008](https://github.com/asalzburger/nodd/blob/5664d16aea2df36222dc0099ba18594cf506304d/docs/decisions/ADR-008-prototype-ecal-forward-aperture.md), [PR70 — open](https://github.com/asalzburger/nodd/pull/70), [PR71 — open barrel prototype](https://github.com/asalzburger/nodd/pull/71) |
| HCAL | Steel–scintillator rough outline; detailed layout follows. | [DES029 envelopes](../design/DES-029-calorimeter-assemblies.md#executed-prototype-budgets-and-layout-limits), [PR69 — merged](https://github.com/asalzburger/nodd/pull/69) |
| FCal | Not yet included. | Future design |
| Muon system + its magnets | Not yet included. | Future design |

Tracker colour blocks show recorded sensitive-group bounds, omitting passive
services. Hatched magnet regions are allocations. ECAL blocks show package
bounds, including inactive regions: the η = 4 target has gaps. Dashed HCAL bounds
are an outline. Polygonal calorimeter radii are apothems at sector centres;
corners extend farther. No field map or combined overlap/performance result is
implied.

[Vector drawing](figures/LAYOUT-001-rz.svg) · [Named inputs and exact source revisions](LAYOUT-001.json) · [All candidates](README.md)

Reproduce with `python3 -B tools/layout_overview/draw.py`; use `--check` to verify
that the SVG matches its inputs. The JSON also records the optional PNG command.
