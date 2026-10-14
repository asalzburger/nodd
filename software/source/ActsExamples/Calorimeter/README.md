# Local calorimeter ActsExamples algorithms

Digitization, clustering, FastJet and EDM4hep converters are migrated from the
existing ACTS fork and retain its Sequencer/whiteboard contracts. Pure helpers
live in ../../Calorimeter and transient event data in ../../EDM. Persistent
EDM4hep/podio and FastJet are provided by the existing node's Spack dependencies.

See ../../Calorimeter/README.md for the retained contracts, tests and Python
steering commands. All current C++ controls are retained without changing their
expected numerical or identity/relation checks. No new response calibration or
scientific acceptance is claimed by moving the source.
