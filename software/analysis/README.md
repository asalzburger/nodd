# Job output analysis

`check_geometry.py` compares saved Gen3 source identities, frames, bounds and
native pipe material with the retained DD4hep entity inventory. `make analysis`
uses the outputs from `make geometry` and the current detector build.

`inspect_calorimeter.py` lists event/metadata entries in persisted ROOT files;
`make calorimeter-analysis` inspects the Python-steered synthetic job output.
Numerical and relation controls remain in the retained C++ test suite.
Generated reports stay under build/jobs. Analysis does not change accepted
reference evidence or grant scientific/design approval.
