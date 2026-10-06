# Integrate trimmed single and quad pixel baseline into main

Selected user request: “Can you make sure that everything from PR41 that is needed to achieve the 4 singles + quad layout is merged — and that main now carries this as the standard baseline?” This authorizes integration and ordinary merge; it does not grant scientific sign-off.

Started from the clean prototype branch at38255171eaa3e211da3bc1eebfcaead3b749807a. PR41 had closed without merging; PR42 mixed support, PR43 eta apertures and PR44 DD4hep merged into that branch. Main carried PR40 atdbcc3b20d5062e6f5014ead06cd849f2eb9fb26e. Existing PR46 is the integration path. Its template title failed the naming gate.

Ordinary merges brought main/PR40 and the executed DES019 contract clarification together. Integration exposed stale pins and then fractional mixed-export datums. Reviewed input changes only add PR40 datums/provenance (and their dependent pins); no retained science artifacts were refreshed. Rigid complete-disc shifts retain frozen local positions/axes/IDs/materials, while transport spans follow the new datums. A default CLI regression ensures5362modules/11806sensitiveareas and four single/two quad source rings with all18 reviewed positions.

Native execution used dirty88757da7466483d857b286496e2404f92315e18f with exact source/config/input/plugin hashes retained in docs/validation/DES-019/main-integration. Build, six CTests and Geant4 initialization succeeded. Independent comparison checked92650module components, and removed-patch exclusion remains above1.563921mm. Twenty optimization, seven support and nine eta controls passed. Early stale-pin/datum/missing-Shapely/historical-input/helper-parsing failures remain in JSON; old artifacts and their hashes are unchanged. Spack registry fingerprints differ, but installed runtime behavior was verified without dependency modifications.

Previously completed eta and DD4hep/TDR usage records were mirrored from the byte-checked primary canonical copies, preserving sources/owners/counters exactly. PR40 shared counters arrived through the ordinary main merge. None are assigned to this new integration task. Current-turn final usage is unavailable while active; usage[] is unknown, not zero. Older project coverage remains partial.

Publication, hosted validation and safe primary-main synchronization are pending. DES016..019 remain DRAFT. Original coverage/guard/warm thermal/service-packing failures and the field/vacuum/vertex/pT hypotheses remain. TDR PR45 is a separate reviewable deliverable.
