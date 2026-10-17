# DES039 — Forward calorimeter design and fit evidence

- Status: **PROTOTYPE evidence**, 2026-10-17; no design acceptance.
- Design: [DES039](../../design/DES-039-common-forward-calorimeter.md); [ADR010](../../decisions/ADR-010-common-forward-calorimeter.md).
- Numerical inputs, exact hashes and full per-ray results: [analytical](geometry.json), [ROOT native](native.json).

## Outcome and scope

A common 1.8 m body fits both pinned layout envelopes. The LAr candidate additionally needs the short, wider EM collar. The physical bore changes from the prior empty80 mm reservation to50 mm. The added collar collector, R298 mm service neck and rear outboard handoff planes are explicit draft amendments. Downstream machine, optical/shower, irradiation and engineering qualification remain open.

Ten standard-library adverse/conservation controls pass. ROOT constructs both signs in each layout, including the02collar and straight service neck, with zero reported overlaps at1e-5mm. The neighbouring calorimeters are conservative circular guards, not complete imported detectors.

## Counts, material and local electronics budgets

| Per component/end | Common body | 02 collar |
| --- | ---: | ---: |
| Finite fibre passages | 24,324 | 22,812 |
| Optical tower outputs | 96 | 96 |
| Physical SiPM pixels | 1,536 | 1,536 |
| Partial represented mass [kg] | 4,840.200 | 1,105.167 |
| Transverse-average sample nuclear λ | 11.3613 | 0.9889 |
| Transverse-average sample X0 | 319.629 | 28.002 |

The partial analytical mass includes exact W/core/buffer and named structural aluminium; it excludes optical fan-out, complete electronics/mounts and external routes. Native ledgers include additional silicon-footprint slabs, coldplates and water-line components, separately identified. Compare common constituent subsets, not mismatched total scopes. Nuclear λ is not pion λ or shower containment.

| Whole layout, both ends | 01 | 02 |
| --- | ---: | ---: |
| Body/collar tower outputs | 192 | 384 |
| Physical SiPM pixels | 3,072 | 6,144 |
| Partial mass [kg] | 9,680.400 | 11,890.735 |
| Nominal local heat incl. conversion [W] | 218.945 | 437.890 |
| Adverse local heat incl. conversion [W] | 916.977 | 1833.954 |

The current/power assumptions are design stresses, not measured or end-of-life device specifications. Beam heat is unknown. The ideal3K water-equivalent flows per module/end are 0.008722 / 0.036527kg/s. A cold operating fluid, hydraulic network, headers and external plant are not qualified.

## Finite directional material and transition controls

The retained scan uses13eta values,64offset phi values and both sides per component/layout. The sampled min/mean/max exclude the exactly aligned clamshell joints; an explicit phi90degree adverse control records zero matrix depth. Do not describe the sampled range as a full-azimuth guarantee. The64phi grid is a deterministic screen, not statistical acceptance.

| Layout / eta | Body nuclear λ, sampled min–max | HCAL envelope path [mm], min–max |
| --- | ---: | ---: |
| LAYOUT-001 / 3.4 | 0.000–0.000 | 1499.2–1499.2 |
| LAYOUT-001 / 3.6 | 3.382–3.789 | 834.7–888.2 |
| LAYOUT-001 / 3.8 | 11.180–11.506 | 0.0–0.0 |
| LAYOUT-001 / 4 | 11.257–11.790 | 0.0–0.0 |
| LAYOUT-001 / 5 | 11.207–12.066 | 0.0–0.0 |
| LAYOUT-002 / 3.4 | 0.000–0.000 | 1499.2–1499.2 |
| LAYOUT-002 / 3.6 | 0.565–0.675 | 1498.1–1498.1 |
| LAYOUT-002 / 3.8 | 10.910–11.523 | 1081.8–1147.1 |
| LAYOUT-002 / 4 | 11.046–11.560 | 0.0–0.0 |
| LAYOUT-002 / 5 | 10.808–12.066 | 0.0–0.0 |

HCAL entries are geometric envelope distances only; no steel/scintillator sampling or response is inferred from them. LAYOUT-001 has a partial-depth handover;02uses the collar for the EM transition. Ateta5the narrow-body sample front is only6.36/10.63mm from the sensitive inner edge; the collar has4.43mm. Straight path depth alone cannot establish lateral containment. A direct primary can miss all fibre cores at some angles while its shower may still generate fibre light; neither crossing count nor its absence is particle efficiency.

## Optical/readout allocation screen

All exact integer fibres map to physical6mm sensor pixels. Maximum fibres per optical tower are 386 / 344; the5x5pixel ferrule limit is respected.

The cosine fan-out model has minimum individual-fibre bend radii 187.369 / 73.266mm, against the70mm project choice. The collar has limited bend margin. This checks endpoints and individual curves, not complete fibre-fibre collision, connector manufacturing, transmission or irradiated optical attenuation.

## Executed native geometry

ROOT6.40.04 / Python3.14.5 were exercised in the existing reverified Spack runtime. The node registry detected changed setup/lock fingerprints; actual ROOT, DD4hep and DDG4 imports and data-directory availability were checked before relying on the environment. The actual geometry audit is ROOT-only. No DD4hep factory, detector readout decoder or Geant4 transport is claimed.

Native CheckOverlaps(1e-5mm) found no overlaps/extrusions in either isolated layout. There were72IPboundary rays plus18axial fibre-core/short-plug/absorber controls. The maximum path residual was8.57e-11mm; common constituent volumes and masses agree to1.12e-7mm3 /2.44e-10g. Both subprocesses exited0. An earlier PyROOT ownership teardown failure was corrected; a saved report with nonzero process exit is now rejected. Exact commands, ROOT export hashes, executed source hashes and the differences from the initial pinned scientific snapshot are retained in native.json.

**Native geometry omits** the optical loom, collar collector elbows and itsconnection to the neck, complete device/FE/gas/electrical geometry, outboard manifolds, external load frames and full neighbouring detectors. Straight neck pipes and conservative envelope guards are present. Analytic elbow bounds do not become native elbow evidence.

## Reproduction and independent assessment

See [tool instructions](../../../tools/forward_calorimeter/README.md). Retained report generation is deterministic for identical source bytes. The package and two layout PNGs were visually inspected; corrected cartridge polygon ordering and small text before delivery.

A [separate PhysVal assessment](physval.md) of exact revision `3c5eded29c1186e7dbd213ac5aab913376babc05` found no blocking issue for the scoped prototype fit. Two minor dossier allocation/rotation wording issues were corrected without changing scientific geometry. The reviewer independently checked38finite-cylinder rays and source hashes. No AI assessment grants human design sign-off.

Not run: full combined native construction, DD4hep/readout integration, Geant4 optical/shower transport, detector performance, dose/EOL tests, deposited beam heat, thermal/hydraulic calculations, structural/access and machine qualification.
