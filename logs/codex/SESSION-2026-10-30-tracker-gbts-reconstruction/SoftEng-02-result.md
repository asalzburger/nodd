# RECO-SoftEng-02 — measured-SP histogram diagnosis

Read-only review d166334b93ec19692e0c433cf03dd343d648f135. No production edits,
shared changes or simulation campaign. Measured-SP replay: control5/10seeded;
triplet settings9/10; histogram disabled alone9/10; no histogram+minSeedLevel2
10/10. Event0graph changes3edges/1connection/level2→6edges/4connections/level3.
Event7has3physical groups, so needs lower seed level. Rotations, reflection,
reordering and removing repeated same-group hits do not remove histogram loss.
Small measured-z translations expose histogram-boundary sensitivity. Broad cuts,
no triplet validation and loose filter alone have no effect. Exact internal bug
or upstream fix was not proven by ACTS Core instrumentation; disable only this
optional cut and retain control. Source GraphBasedTrackSeeder.cpp208–209,
317–318,400–401,562–592,688–689,967–1006. Replay input eventSHA
 a2db9af94c38b37425262c45399463b432ce0ce5b267fcec7de69bb22c1b7de5;
geometrySHA1fd4d83de6519b64c3ac93dcc431398d9a07c82af32223cae03cd8983bc41c01.
Numericaldiagnostics retained; ad-hoc launcher scripts stay ignored. This is
author diagnostic support, not an independent final software review.
