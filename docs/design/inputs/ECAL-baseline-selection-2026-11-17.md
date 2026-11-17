# nODD ECAL working-baseline selection

2026-11-17. Governing designs: DES-032 and DES-033. **Human-selected working baseline; engineering qualification remains open.**

**FACT - recorded human direction:** [PR145 comment6951330371](https://github.com/asalzburger/nodd/pull/145#issuecomment-6951330371), posted by `asalzburger-review`, selects the ALLEGRO-style LAr ECAL with a 400 mm barrel/endcap warm gap as the new nODD baseline. The comment attributes the decision to discussion with reviewer Michael Duehrssen and requests a four-series response comparison. This record attributes that statement to its actual author; it does not create an independent sign-off by another person.

**NODD DESIGN CHOICE - selected by that direction:** develop LAYOUT-002 with the reduced-gap LAr ECAL as the nODD electromagnetic working baseline. The barrel warm end stays at abs(z)=4100 mm. The complete endcaps move 400 mm inward, from abs(z)=4900-5860 mm to 4500-5460 mm. Keep internal materials, local placements and readout as in the retained gap study. Retain realistic Si-W, its physical staggering, and ODD as comparison references.

The decision supersedes Si-W as the selected ECAL technology and the source-era 800 mm front-gap choice. It does not certify a complete detector assembly. [The gap study](../../validation/lar-gap10k/README.md) is an isolated ECAL-only numerical comparison. [The routing prototype](../../validation/lar-routing-dd4hep/README.md) validates representative pipe material/navigation, while complete ports, displaced local services, boards/supports, collar/FCAL, tracker/magnet and HCAL interfaces remain to be integrated and qualified. **INFERENCE from the declared envelopes:** the existing collar allocation conflicts with part of the inward-shifted endcap; it must be redesigned or repositioned before a combined fit can be claimed.

The maintained combined DD4hep exporter and existing full-layout R-Z drawings still reproduce the 800 mm integration control. This documentation/plot response does not silently change their dimensions or claim that their old native-union proof covers the selected 400 mm design. The [layout main page](../../layouts/README.md) identifies the selected baseline and that implementation boundary. The report's routing schematic depicts the 400 mm target separately. Formal design lifecycle states remain DRAFT/PROTOTYPE; identified human engineering acceptance remains separate.

## Requested comparison contract

The single SVG compares relative raw energy-response width versus abs(eta), with
R = summed saved active-hit energy / primary total energy and width = sample SD(R) / mean(R). It is the available sigma(E)/E response-width proxy, including zeros and tails, rather than fixed-energy intrinsic or reconstructed resolution.

Before deriving the display, fix uniform abs(eta) bins of width 0.05 from 0 to 3 for all three matched 10,000-electron Si-W/original, Si-W/staggered and LAr/400 mm series. Preserve the original primaries and saved-hit sums. Use 1000 shared whole-primary bootstrap replicates with seed13001000 and pointwise 95% percentile endpoints; no transport, calibration, fit or selection retuning.

ODD has no matched broad-spectrum 10k cohort in retained evidence. Plot its existing 20 GeV/c electron measurements at eta0/1/2 (200 per point, phi0.123 rad) as unconnected reference markers with their own retained 95% intervals. Label the cohort difference on the figure. Do not substitute the original realistic Si-W scan for ODD or draw an unsupported continuous ODD curve. The three broad-spectrum series and the fixed-energy reference are not a four-way paired significance test.
