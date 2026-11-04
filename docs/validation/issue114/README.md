# Issue #114 — restored calorimeter I/O

Date: 2026-11-04. Scope: software plumbing, with no detector parameter or
tracker-path change. Starting main revision:
`cd3ec20da56537617ac6fbbcf28bd6f28104cc64`.

Executed implementation revision: `8652406ec992178a16f419b41d95aed73f40f1bc`. The accompanying session record retains the source/build checks. Its
origins are ACTS fork `8adca5eec180515a23d58d132a1e17e317a59e67` and nODD
PR #80 head `530080cfe16c7513228bf60238b99d4b9938538a`.
[Imported-source notice](../../../software/source/NOTICE.md) describes the
bounded changes. No raw event files or run logs are committed.

## Environment actually used

- Node `acts-mac-studio-01.cern.ch`, macOS arm64.
- AppleClang 21.0.0.21000334, CMake 4.4.4, Ninja.
- Pristine ACTS source
  `../nodd-software-layout/software/submodules/acts`, exact HEAD
  `355ea68493b326956756c9386d2fd9eaf9328568`.
- Existing matching build `../nodd-software-layout/build/acts`; only its
  Core, ExamplesFramework and ExamplesIoPodio libraries are linked.
- Existing Spack environment `ci-dependencies`: EDM4hep 1.1.1 `/bsgcccc`,
  podio 1.8 `/hg64alv`, ROOT 6.40.04 `/szgev3e`, Boost 1.90.0 `/yi2vs77`,
  Eigen 5.0.1 `/4hly7in`.

The required Spack preflight returned exit 2: recorded setup/lock fingerprints
had changed, and full DD4hep/Geant4 sources were unverified. The user was warned
before dependent work. `setup_spack`, `spack env status`, installed spec queries,
pristine source checks, actual compilation and native tests reverified the
capabilities needed here. Sandbox `sysctl` warnings and CMake CMP0144 developer
warnings were retained; neither prevented these checks. No shared install was
changed. The separate dirty `work/dev/acts-nodd` checkout at `555c66e` was
inspected and preserved; it is not the executing source/build.

## Reproduction

From the nODD checkout in a fresh zsh shell:

```sh
python3 skills/acts-spack/scripts/preflight.py --require-sources
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP
setup_spack
spack env status
spack find --format '{name}@{version} /{hash:7} {prefix}' edm4hep podio root eigen boost
cmake -S software/source/ActsExamples/Calorimeter \
  -B /tmp/nodd-calorimeter-edm114-build -G Ninja \
  -DNODD_ACTS_SOURCE=/Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-software-layout/software/submodules/acts \
  -DNODD_ACTS_BUILD=/Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-software-layout/build/acts
cmake --build /tmp/nodd-calorimeter-edm114-build --parallel 4
ctest --test-dir /tmp/nodd-calorimeter-edm114-build --output-on-failure
```

The first preflight intentionally reports its independent registry status;
subsequent commands must be evaluated separately. Substitute matching local
source/build paths on another verified node. CMake fetches nothing and requires
an existing build configured from the exact checked source.

## Executed results

All four CTest targets pass:

| Target | Result |
| --- | --- |
| CalorimeterEDM4hep | Nine cases: input expansion/units/cell centres, hit persistence and weighted truth relations, empty collections, wrong types/geometry, malformed contributions/provenance, source mapping, float overflow/underflow and invalid config. |
| CalorimeterEDM4hepClusters | Eight cases: cluster relations and sidecars, malformed clusters and partial-output rejection, overflow, persistent-hit mapping, empty collections, metadata preservation/collisions/config. |
| CalorimeterAlgorithmSkeletons | Two cases: invalid I/O config and explicit failure without outputs, including empty input collections. |
| CalorimeterEDM4hepRootRoundTrip | Three events through real podio ROOT input, ActsExamples sequencer/converters and ROOT output; verifies 64-bit IDs, units, cluster→hit and hit→simhit→contribution→MC relations, sidecars, original frame parameters and schema-2 unimplemented-stage metadata. |

The ROOT test supplies fixed native hit/cluster fixtures. It does not invoke
either processing skeleton, simulate a response, apply thresholds, construct
connected components or calibrate detector data. All native numerical values
are explicitly synthetic test inputs. Existing converter conservation and
provenance validation is retained.

Two negative configuration controls pass: an ACTS source at `8adca5e` is
rejected with configure exit 1; the correct source paired with the unrelated
`work/build/acts-nodd` build is rejected with configure exit 1. The normal
source/build pair configures successfully. `otool -L` confirms the fixture
links no former calorimeter response/clustering/jet libraries or FastJet.

The first build failed because the example included ACTS `PodioUtil.hpp`,
which pulls tracker-specific generated EDM headers. It was corrected to use
podio ROOT reader/writer directly, then rebuilt and tested successfully. No
tracker source or generated header was changed.

## Limits and follow-up

Digitization and clustering are I/O/configuration skeletons whose execution
throws `std::logic_error`. They produce no successful empty output. Realistic
response, calibrated clusters, topology/CLUE, jets, EDM extensions and a cell-ID
service require follow-up work. These I/O checks establish no shower,
resolution, engineering sign-off or full-detector acceptance. Geometry tests
belong to the separately consolidated ECAL/HCAL/FCAL campaign.
