# GEN3MAP-PhysVal-01 retained completed assessment

Source: completed visible child turn 01a177c4-4d5f-7cd3-97fd-1d46eadbf769. Exact target a99b63cba68f8c66723df6ed5c55935e6675971a. Explicit fallback mandate; native profile loading is not claimed.

**GEN3MAP-PhysVal-01 — independent review complete**

Reviewed revision: `a99b63cba68f8c66723df6ed5c55935e6675971a`. Read-only; no files changed. No blocking defects found for the requested **first-step plots and surface proposal**. This is not detector acceptance or validation of a finished map.

Findings requiring follow-up before production mapping:

- **Medium:** 968,999 passive pixel steps lack a same-ray, same-layer sensitive crossing and carry **76.21% of pixel passive X₀**. Their provisional before assignment cannot establish sensor-facing order. This is accurately disclosed in `docs/validation/gen3-material-mapping/README.md:127` and implemented at `survey.py:194–226`.
- **Medium:** Choosing a finite portal before/after the material midpoint does not establish preservation of order relative to intervening sensitive planes, especially shared two-face backing. The report explicitly retains this limitation at `README.md:135–140`; ownership and segmentation remain necessary.
- **Low:** The recording’s geometry revision, seed and original command are unavailable. Matching compact/factory hashes and density checks support the selected comparison geometry but cannot establish its identity with the recording geometry. The report states this correctly at `README.md:142–154`.

Actual checks:

- **14 portable tests passed**, executing exact target-commit source retrieved with `git show`.
- Independently streamed **all 100,000 tracks / 17,137,021 steps** using closed-form distances to finite cylinders/annuli rather than the implementation’s segment projection. Exact remote counts at **5 / 10 / 20 mm** matched: **3,654,429 / 962,351 / 376,735**. Passive X₀ fractions matched **78.2652% / 62.5766% / 46.7871%**.
- Recomputed full component counts, passive mean **1.1241328378816744 X₀**, and per-track X₀/λI closure.
- Replayed the first 5,000 tracks’ raw midpoint coordinates, scatter categories and remote flags exactly.
- Verified input hashes for recording, labels, classification and native export; committed portal/volume catalogues equal the hashed native export.
- Verified budget/count partitions, cluster/region totals, **118 candidate portals / 101 nearby**, and **121 unique nonzero ACTS geometry IDs**.
- Inspected pinned recorder source: positions are pre-step coordinates, confirming the midpoint correction. Inspected native adapter/factories: +w is support-facing; native silicon slabs and the Be cylinder are retained separately.
- Visually inspected three pinned PNGs; legends, portal overlay and remote-region locators are readable.

The strict downstream-majority rule and finite directional selection are supported by code and retained evidence. The provisional 10 mm criterion is clearly labeled and accompanied by threshold sensitivity. No new native export, simulation, material-map replay or reconstruction validation was run. The coordinator’s later portable CSV exporter is outside this pinned assessment.
