# Independent integration assessment

Assignment `DES043-Integration-PhysVal-01` assessed exact source `d6c4d0ddfa9e14129a3f4c426fced7c4cee0dcc4`, read only. The reviewer inspected primary producers/configuration before reported outcomes. No native job, source edit or further delegation was performed. Later dirty design/layout text was excluded from this fixed-revision review.

The review found no demonstrated geometry defect. Sixteen portable tests passed across barrel integration, shared services, Gen3 guards and complete default/historical exports. The reviewed files matched all ten pinned Git-object hashes. The selected 46,682-plane/54-group inventory includes all 4,752 new EC planes; the historical control retains 46,250/54. Barrel windows, u=±12 mm inserts and straight/U-turn cuts, standard readouts and preserved pixel/long-strip branches were checked.

Independent route counting found 1,008 power feeds, 1,584 optical groups, 864 leaf loops, 720 boards and 136 bulk pipe pairs across both ends. Independent route integration reproduced every allocated constituent with maximum fractional difference 2.8×10⁻¹⁵:

| Constituent | Volume [L] |
| --- | ---: |
| Copper | 55.021709 |
| Polyimide | 51.632650 |
| Internal package air | 21.856388 |
| Silica | 18.848069 |
| Titanium | 15.231202 |
| CO₂ | 29.702672 |

Recovering constituents from the generated mixture density/fractions independently conserved the non-air payload. Unused-corridor air is counted once, and packing factors reserve space without scaling material.

Three medium validation gaps were demonstrated at this revision:

1. Empty source/probe manifests can pass the old checker; consumed material/XML bytes lack complete producer binding.
2. An unexpected passive copper solid can escape known-role counts. A portable adverse mock demonstrated this gap; it did not establish an actual extra solid.
3. Native density/name comparison does not establish native mixture fractions.

The supplementary `audit_payload.py` closes these evidence gaps by comparing the complete consumed export with fresh producer bytes, requiring source/contact coverage, checking every nonassembly solid and resolving native elemental fractions. Its actual execution is identified separately in the [compact results](summary.json). Geometry/input/library bytes must stay unchanged so the expensive overlap pass remains applicable. No test tolerance is relaxed and the earlier checker is not relabeled as having performed these extra checks.

The assessment does not certify the concurrently executed native overlap/ACTS jobs, full material map, new-geometry reconstruction, cable/ASIC feasibility, thermal/hydraulic qualification or engineering acceptance. The coordinator reconciles the actual outcomes and current design wording in the integration report.
