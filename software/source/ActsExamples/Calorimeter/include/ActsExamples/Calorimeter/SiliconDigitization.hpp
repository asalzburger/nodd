// Copyright (C) 2026 CERN for the benefit of the ACTS project
// SPDX-License-Identifier: MPL-2.0
#pragma once

#include <cstdint>
#include <string>
#include <vector>

#include "Acts/Definitions/Algebra.hpp"

namespace ActsExamples {

/// Explicitly selected, unsigned PROTOTYPE energy response. Numerical defaults
/// except mipEnergy follow MarlinReco255967eb's RealisticCaloDigiSilicon.
/// This is a deposit-equivalent cell-energy scale, not shower calibration.
struct SiliconDigitizationConfig {
  std::string executable;
  double mipEnergy =
      0; ///< ACTS energy; mandatory measured/configured MIP scale.
  double pairEnergyEv = 3.6;
  double noiseMip = 0;
  double dynamicRangeMip = 2500;
  double thresholdMip = 0.5;
  std::uint64_t seed = 117;
};

struct SiliconDigitizationCell {
  std::uint64_t cellId = 0;
  Acts::Vector3 position = Acts::Vector3::Zero();
};

/// Check the physical/numerical configuration without executing a backend.
void validateSiliconDigitization(const SiliconDigitizationConfig &config);

/// Call the separate GPL executable; no GPL implementation is linked into the
/// MPL library. Input energies are ACTS units; output values are signed MIPs
/// before threshold selection. Original float arithmetic and CLHEP draws are
/// executed by the backend. Empty cells explicitly bypass pair statistics,
/// then use original electronics noise. This is an all-channel extension.
std::vector<double>
runMarlinSilicon(const SiliconDigitizationConfig &config,
                 const std::vector<double> &depositedEnergies,
                 std::uint64_t eventNumber);

} // namespace ActsExamples
