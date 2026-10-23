# PR94 cross-platform export correction

The [CI comment](https://github.com/asalzburger/nodd/pull/94#issuecomment-6361605900)
refers to [failed run39924882061](https://github.com/asalzburger/nodd/actions/runs/39924882061).
Ubuntu24.04/Python3.12.15 differed from macOS in the last bits of a reconstructed
angle. Only the frozen-export comparison failed; all other14 focused tests passed.
The issue was reproduced locally by moving `math.atan2` results by one ULP.

Source fix: `4605ad6ba160c478a324ca1aa30a7cd3c934cd4e`. The exporter reads the
original source angle and projects with its pinned basis. A 60-digit Decimal
sine/cosine series and square root keep serialized expansion diagnostics independent
of libm. The byte-for-byte frozen-artifact test and all existing tolerances remain.
The added regression moves sin/cos/atan2/dist results by one ULP and requires
identical output bytes. All16 controls pass on macOS Python3.11.15 and3.14.6.

[source-comparison.json](source-comparison.json) verifies exact equality of all936
source entities, IDs and36 coil definitions with previous head5263d48. Current XML
is28,907 bytes;22 shared shapes,21 phi orbits,56 rows and6 genuine z-loop rows are
unchanged. The earlier [template evidence](../dd4hep-templates-2026-10-23/README.md)
retains its original bytes and hashes.

## Committed native replay

The [run](run.json) and [geometry report](geometry-validation.json) identify the
clean source commit above (`source_dirty:false`) and current input/library hashes.
The native factory is unchanged and its previously built library is reused.
Fresh installed-runtime checks verified DD4hep1.38, ROOT6.40.04 and Geant411.4.3
with12 present datasets. The registry preflight warned of changed setup/lock
fingerprints; no shared dependency installation was modified.

- 936 source chambers and stable identifiers pass;22 unique native Solids/Volumes.
- Maximum native vertex residual:1.0087767680389479e-14 m, within the unchanged
  1e-10 m tolerance. Export expansion residual:1.2623387138745463e-14 m, within1e-12 m.
- 288 coil primitives and25,248 occupancy probes pass; zero overlaps at0.00001 mm.
- 1,000 persisted20 GeV gamma events, seed92393, FTFP_BERT, DDSim `uniform`
  (flat polar theta and azimuth).

The [ROOT truth comparison](transport-comparison.json) checks the retained baseline
ROOT digest and current ROOT digest, exactly matching primary momentum banks and
event particle multiplicities. Both contain only the MCParticles branch, one
parentless PDG22 primary per event, and a zero primary vertex. ROOT binaries stay
in ignored local cache. Raw logs are retained beside these reports; DDSim is gzipped.

Reproduce with the [prototype commands](../../../../prototypes/muon/README.md),
using a fresh output directory. The source/compact are authoritative; the fixed
arithmetic introduces no new dependency. The 60-digit series is an export tool,
not an installed detector arithmetic requirement.

This is coordinator validation of a tightly dependent CI correction, with no new
independent specialist assessment. DES039/DES040 remain DRAFT. Empty nonsensitive
Air envelopes give no drift-tube/material/response or engineering acceptance.
