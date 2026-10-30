// Numerical compatibility controls; synthetic values are test fixtures only.
#include "SafeBetheHeitler.hpp"
#include "ActsPlugins/FpeMonitoring/FpeMonitor.hpp"
#include <bit>
#include <cfenv>
#include <cstdint>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <vector>

#pragma STDC FENV_ACCESS ON

namespace {
void require(bool value, const char* message) {
  if (!value) throw std::runtime_error(message);
}
bool same(double a, double b) {
  return std::bit_cast<std::uint64_t>(a) == std::bit_cast<std::uint64_t>(b);
}
double originalLoss(double u, double scale, double energy) {
  const double z = std::exp(-u);
  return std::abs(scale * energy * (z - 1.));
}
double safeLoss(double u, double scale, double energy) {
  return std::abs(scale * energy * nodd::safe_fatras::energyFractionMinusOne(u));
}
void compareParticle(const ActsFatras::Particle& first, const ActsFatras::Particle& second) {
  for (int i = 0; i < 4; ++i) {
    require(same(first.fourMomentum()[i], second.fourMomentum()[i]), "Particle momentum changed");
    if (i < 3) require(same(first.position()[i], second.position()[i]), "Particle position changed");
  }
  require(first.particleId() == second.particleId() && first.outcome() == second.outcome(), "Particle identity/outcome changed");
  require(same(first.time(), second.time()), "Particle time changed");
}
}  // namespace

int main() {
  require(std::fegetround() == FE_TONEAREST, "Test requires round-to-nearest");
  const std::vector<double> edges = {0., std::numeric_limits<double>::denorm_min(),
      std::numeric_limits<double>::min(), 1.e-20, 1.e-10, .1, 1., 36., 38.,
      std::nextafter(40., 0.), 40., std::nextafter(40., 100.), 41.,
      700., 708., 710., 744., 745., 800., 1.e4, 1.e100,
      std::numeric_limits<double>::max()};
  std::uint64_t comparisons = 0;
  auto compare = [&](double u) {
    require(same(std::exp(-u) - 1., nodd::safe_fatras::energyFractionMinusOne(u)), "Rounded fraction changed");
    for (double energy : {.000511, 1., 123.25, 1.e6}) {
      for (double scale : {.5, 1., 1.25}) {
        require(same(originalLoss(u, scale, energy), safeLoss(u, scale, energy)), "Sampled energy loss changed");
        ++comparisons;
      }
    }
  };
  for (double u : edges) compare(u);
  // Stratify the entire positive finite binary64 bit-pattern range, including
  // every exponent. This supplements the analytic all-u rounding proof.
  std::mt19937_64 values(47541);
  for (int exponent = 0; exponent < 2047; ++exponent) {
    for (int sample = 0; sample < 64; ++sample) {
      const std::uint64_t bits = (std::uint64_t(exponent) << 52) | (values() & ((std::uint64_t(1) << 52) - 1));
      compare(std::bit_cast<double>(bits));
    }
  }

  // Compare the actual original/safe operators, including every RNG draw,
  // photon kinematics and parent update. Thin and very thick slabs are fixtures.
  const auto material = Acts::Material::fromMolarDensity(200., 200., 28.0855, 14., .001);
  std::uint64_t operatorComparisons = 0;
  for (double thickness : {.001, .01, 1., 20., 80., 800.}) {
    Acts::MaterialSlab slab(material, 200. * thickness);
    for (std::uint64_t seed = 0; seed < 1000; ++seed) {
      std::mt19937_64 originalRng(seed), safeRng(seed);
      ActsFatras::Particle original(ActsFatras::Barcode{}, Acts::PdgParticle::eElectron);
      original.setAbsoluteMomentum(100.).setDirection(Acts::Vector3(.2, .3, 1.).normalized());
      auto guarded = original;
      const auto originalPhoton = ActsFatras::BetheHeitler{}(originalRng, slab, original);
      const auto guardedPhoton = nodd::safe_fatras::SafeBetheHeitler{}(safeRng, slab, guarded);
      require(originalRng == safeRng, "RNG engine state/order changed");
      compareParticle(original, guarded);
      compareParticle(originalPhoton[0], guardedPhoton[0]);
      ++operatorComparisons;
    }
  }

  // Positive control proves the installed libm really signals this underflow.
  std::feclearexcept(FE_ALL_EXCEPT);
  volatile double largeU = 800.;
  volatile double original = originalLoss(largeU, 1., 123.25);
  (void)original;
  require(std::fetestexcept(FE_UNDERFLOW), "Original underflow positive control did not signal");
  std::feclearexcept(FE_ALL_EXCEPT);
  volatile double guarded = safeLoss(largeU, 1., 123.25);
  require(guarded == 123.25, "Guarded extreme loss changed");
  require(std::fetestexcept(FE_ALL_EXCEPT) == 0, "Guarded path raised a hardware FP flag");

  ActsPlugins::FpeMonitor monitor;
  volatile double monitored = safeLoss(largeU, 1., 123.25);
  (void)monitored;
  require(!monitor.result().encountered(ActsPlugins::FpeType::FLTUND), "Guarded path triggers native FPE monitor");
  std::cout << "PASS: " << comparisons << " bitwise energy-loss comparisons, "
            << operatorComparisons << " exact parent/photon/RNG comparisons; original underflow positive control; guarded hardware/native FPE checks\n";
}
