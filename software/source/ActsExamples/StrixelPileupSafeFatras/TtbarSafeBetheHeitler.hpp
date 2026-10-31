// Adapted from ACTS355ea684 BetheHeitler.hpp and StandardInteractions.cpp.
// Copyright (C) 2016 CERN for the benefit of the ACTS project.
// This Source Code Form is subject to the Mozilla Public License, v. 2.0.
// See https://mozilla.org/MPL/2.0/.
// DES041 isolated PROTOTYPE; distinct types, no upstream symbol replacement.
#pragma once

#include "ActsFatras/Physics/StandardInteractions.hpp"
#include "nodd/ttbar_safe_fatras/ZeroObservableGammaDistribution.hpp"

#include <limits>

namespace nodd::ttbar_safe_fatras {

static_assert(std::numeric_limits<double>::is_iec559 &&
              std::numeric_limits<double>::digits == 53);

/// This benchmark requires the unchanged IEEE round-to-nearest environment.
/// For 0<=u<2^-54, exp(-u) rounds to 1, so exp(-u)-1 is exactly +0.
/// For u>40, exp(-u)<exp(-40)<2^-54, so binary64 exp(-u)-1 rounds to
/// exactly -1. Avoid libm intermediates that underflow even when their rounded
/// contribution to the sampled loss is zero. All random draws remain unchanged.
inline double energyFractionMinusOne(double u) {
  if (0. <= u && u < 0x1p-54) return 0.;
  if (u > 40.) return -1.;
  return std::exp(-u) - 1.;
}

struct SafeBetheHeitler : ActsFatras::BetheHeitler {
  template <typename generator_t>
  std::array<ActsFatras::Particle, 1> operator()(
      generator_t& generator, const Acts::MaterialSlab& slab,
      ActsFatras::Particle& particle) const {
    ZeroObservableGammaDistribution gDist(
        slab.thicknessInX0() / std::numbers::ln2, 1.);
    const double u = gDist(generator);
    const double sampledEnergyLoss =
        std::abs(scaleFactor * particle.energy() * energyFractionMinusOne(u));

    std::uniform_real_distribution<double> uDist(0., 1.);
    ActsFatras::Particle photon =
        bremPhoton(particle, sampledEnergyLoss, uDist(generator),
                   uDist(generator), uDist(generator), uDist(generator));
    particle.setDirection(particle.direction() * particle.absoluteMomentum() -
                          photon.energy() * photon.direction());
    particle.loseEnergy(sampledEnergyLoss,
                        ActsFatras::SimulationOutcome::KilledInteraction);
    return {photon};
  }
};

using StandardBetheHeitler = ActsFatras::ContinuousProcess<
    SafeBetheHeitler, ActsFatras::detail::SelectElectronLike,
    ActsFatras::detail::SelectPMin, ActsFatras::detail::SelectPMin>;

using ChargedInteractions = ActsFatras::InteractionList<
    ActsFatras::detail::StandardScattering,
    ActsFatras::detail::StandardBetheBloch, StandardBetheHeitler>;

inline ChargedInteractions makeChargedInteractions(double minimumAbsMomentum) {
  ChargedInteractions processes;
  processes.get<ActsFatras::detail::StandardBetheBloch>()
      .selectOutputParticle.valMin = minimumAbsMomentum;
  processes.get<StandardBetheHeitler>().selectOutputParticle.valMin =
      minimumAbsMomentum;
  processes.get<StandardBetheHeitler>().selectChildParticle.valMin =
      minimumAbsMomentum;
  return processes;
}

}  // namespace nodd::ttbar_safe_fatras
