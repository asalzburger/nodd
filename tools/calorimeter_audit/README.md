# Calorimeter static hardware audit

Reproduce [DES027](../../docs/design/DES-027-calorimeter-description-assessment.md)
without new dependencies or detector execution:

```sh
python3 -B tools/calorimeter_audit/audit.py --odd-dir "$odd_source_directory"
python3 -B -m unittest discover -s tools/calorimeter_audit -p 'test_*.py' -v
```

The required clean source files are pinned to existing catalogue revision
`c167363f3d4ad1540a577af99071283caf54f3a6`. A different Git HEAD or modified
input file fails explicitly. No clone, source installation or package adoption
is performed. Source byte hashes and the auditor hash accompany the result.

XML dimensions are evaluated with whitelisted arithmetic in millimetres;
unknown names and executable expressions are rejected. Stack depths are sums
over **all** repeated layers. Polygon boundary interpretation follows the
inspected factories, with distinct apothem/corner meanings for barrel/endcap
inputs. Normal areal mass is thickness × density; it is not total detector mass.
The mixture recipe is checked for normalized fractions.

This is static characterization. It does not construct DD4hep solids, qualify
supports/cooling/power, infer response, or install inherited ODD calorimeters
into the maintained nODD tracker entry point. The report lists exactly what
must be designed and validated before such integration.
