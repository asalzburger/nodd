# SESSION-2026-10-13-layout002-lar-endcaps

Human requests two LAr alternative PRs and LAYOUT-002 on the layout main page.
This second branch contains endcap/turbine and complete candidate integration,
stacked on the barrel core879e836. First branch continues services/evidence and
will be normally merged into this branch before final PR review. Root retains
SiW LAYOUT-001, inner3T target and no muon system; forward coverage is marked
uncovered with a future FCal reservation. No new externals or human sign-off.
Current exact root/child counters unavailable; usage empty/unknown.

Primary-source and read-only SysArch/PhysVal handoffs are curated in the barrel
journal, with explicitly new gap/bath/envelope adaptations in DES033. Prototype
endcap source geometry facts are read independently from official k4geo e1ba7bc3
and actual primary publications; no external factory is imported.

Native role loading not claimed. Implementation contract follows below before
dispatch. Root owns endcap services/scalar config, DES/ADR/layout pages, project
records and publication; SoftEng owns only new model/export/factory/tests/audit.
