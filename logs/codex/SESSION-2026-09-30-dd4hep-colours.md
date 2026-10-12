# SESSION-2026-09-30-dd4hep-colours — Persist material display colours

## Request and scope

The user confirmed geoDisplay worked and asked for meaningful material colours
that survive ROOT export. This visual-only follow-up updates PR #30/DES-012.
The starting revision and preserved unrelated usage files are in the paired JSON.

## Implementation

A separate display.json palette assigns standard ROOT colours by material family,
with opacity for nested supports/services. Cooling tube/coolant daughters now have
explicit attributes. A shared C++ helper applies exact ROOT line/fill indices,
because DD4hep's RGB matching selected an approximate blue even for the requested
colour-wheel RGB. No physical material or geometry parameter was changed.

The new export_root.py writes a ROOT geometry, starts a fresh ROOT-only process,
imports it without the detector factory or recolouring code, and compares all
36550 placed solid volume styles. It is included in CTest. README commands cover
geoDisplay, export and ROOT viewing. SRC-ROOT-TCOLOR records the public predefined
colour reference; DES-012 PB-C13 marks this as a display convention.

## Actual checks and corrections

Spack preflight warned about changed setup/lockfile fingerprints; runtime was
reverified. CMake build and CTest3/3 passed. Every colour/RGB/transparency/fill/
visibility attribute survived export/import. Physical validation is exactly equal
to retained nominal evidence for counts, mass, materials, navigation, IDs,
transforms and overlaps. The report is docs/validation/DES-012/display/results.md.
Previous accepted numerical artifacts were not overwritten.

Failed round-trip attempts exposed unused registered Air volumes (audit now walks
placed geometry), a PyROOT Char_t-to-byte conversion, and approximate DD4hep RGB
matching (fixed with explicit standard indices). No tolerance was weakened.
Interactive GUI rendering was not exercised; the ROOT geometry is ready to view.

## Delivery and usage

Changes are on implementation/dd4hep-pixel-barrel for PR #30. The paired JSON
records changed paths, commands and actual checks. Exact client input/output token
counts were unavailable; usage is empty, not zero. No subagents were used. Session
summary aggregates are not attributed to this bounded follow-up.
