# Independent display colours and effective transparency

- Date: 2026-10-01
- Scope: human-requested display validation correction, DES-012 PB-C13
- Tasks: TASK-SOFT-DD4HEP-PIXEL, TASK-SOFT-NODEHAMMER
- Evidence: [check summary](independent-colours.json)

The user requested that `root_color` may differ from config `rgb`, then also
requested relaxed transparency validation. ROOT/geoDisplay continues to use the
configured ROOT index. Nodehammer and GLB styling use the configured RGB triplet.
Neither ROOT export nor nodehammer import now requires those colours to coincide.
The ROOT export check also accepts effective transparency different from the
conversion of config `alpha`.

The ROOT snapshot retains its actual RGB and transparency. Fresh-process import
must still preserve the entire snapshot. An undefined ROOT colour or incorrect
configured ROOT index still fails. Nodehammer's generated GLB is still checked
against its own RGB/alpha styles; no cross-viewer transparency agreement is
required. This correction neither changes the geometry nor disables checks of
export persistence.

Four display regression checks cover independent RGB, independent effective
transparency, undefined ROOT colours and wrong indices. Seven nodehammer checks
include a deliberately different imported ROOT/config RGB pair. The complete
DD4hep CTest suite passed with the user's edited local palette, and all three
nodehammer export views passed the entity/mesh/unit/RGBA checks. The user's
palette edits were used for testing and preserved locally, not included in this
change. The earlier report and screenshots remain historical evidence for their
recorded palette and workflow hashes.

The existing SRC-ROOT-TCOLOR and SRC-NODEHAMMER provenance is unchanged. This is
an explicit human change to display validation policy, not detector design
approval. Source/config/runtime hashes and actual check totals are retained in
the companion summary; heavy generated artifacts remain under ignored build/.
