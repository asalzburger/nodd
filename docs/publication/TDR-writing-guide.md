# TDR writing guide

- ID: PUB-WRITING-2026-10-09
- Updated: 2026-10-09
- Basis: explicit human editorial direction and the authored TDR revision `279d882179e93b56e522fd6b390c965f6ab18e84`.

The TDR describes the current detector baseline at the accuracy needed for full
simulation. Organize each subsystem around what a reader needs to reproduce its
sensitive geometry, passive material and service distribution.

1. State the selected technology, geometry and material representation directly.
   Describe the current baseline, without recounting intermediate layouts,
   optimization history or unsuccessful attempts.
2. Keep reasoning that explains a simulation-relevant choice: sensor orientation,
   inactive edges, placement, material ordering, service paths or an effective
   representation. Give that reasoning once, beside the choice.
3. Keep dimensions, constituent thicknesses, compositions and densities accurate.
   Use tables for parameter inventories and avoid repeating their entries in prose.
   Distinguish active silicon, sensor substrate and occupied module envelope.
4. Condense mounting and cooling into their physical topology, material,
   placement, dimensions and boundaries. Detailed assembly procedures,
   constraint explanations and thermal derivations belong in supporting design
   records when they do not change the transport model.
5. Describe approximations positively and precisely: what is explicit, what is
   effective, and which quantity the effective model preserves. State current
   assumptions once where needed to interpret the model; simulation fidelity
   does not imply measured detector performance or engineering qualification.
6. Use figures to explain distinct geometry or material features. Put numerical
   detail in a table rather than a long caption. Combine complementary views
   and avoid repeatedly illustrating the same service handoff.

Public literature supports technology claims. Internal revisions, producer and
artifact hashes remain in provenance manifests. Historical checks, including
their outcomes, remain in the validation reports and session journal; those
records retain their traceability independently of the TDR's baseline narrative.

The [pixel shortening proposal](pixel-chapter-shortening-proposal.md) applies
these rules to the current authored chapter and provides text for review.
