# GEN3MAP-SoftEng-01 — explicit SoftEng contribution

Input f0775a2dd3c30f405880a9e7323e4d230c3c4155; bounded source ownership and
runtime contract are in the paired assignment. No native profile loading claimed.

Implemented `export_geometry.py` and eight pure-Python contract tests. Native
export completed at `build/gen3-material-mapping/geometry.json`:45646 sensors,
117 volumes,121 actual portal surfaces (94discs,27cylinders),244 link
subsurfaces,52 layers,469 owner references. Complete ACTS JSON encode/decode
round trip is identical. Independent converter and detector-report centers/axes
agree exactly. All actual portal IDs unique/nonzero; unsupported geometry0.

Runtime source/binary hashes distinguish adapter530080cfe16c7513228bf60238b99d4b9938538a,
ACTS355ea68493b326956756c9386d2fd9eaf9328568, Python3.14.5,ROOT6.40.04,
DD4hep length unit0.1. Native beam-pipe slab preserved. Final exporter SHA is
recorded in retained geometry provenance. No geometry or shared dependency edits.

A corrected provenance module-name typo required one rerun after native
reduction passed; final export is complete. Source syntax/whitespace and eight
contract tests passed. Sensor normals alone do not define physical front;
coordinator supplies the factory support convention. Input scan revision remains
unknown. Portal traversal IDs apply only to this export; merged portal owners
and link partitions must be retained in a future material mapping implementation.
