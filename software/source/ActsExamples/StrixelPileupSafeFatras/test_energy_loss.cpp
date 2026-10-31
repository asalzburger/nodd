// Numerical compatibility controls; synthetic values are test fixtures only.
#include "TtbarSafeBetheHeitler.hpp"
#include "../SafeFatras/SafeBetheHeitler.hpp"
#include <boost/multiprecision/cpp_bin_float.hpp>
#include "FailureAudit.hpp"
#include "ActsPlugins/FpeMonitoring/FpeMonitor.hpp"
#include <bit>
#include <cfenv>
#include <cstdint>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <vector>

#ifdef NODD_TEST_STRICT_FP
#pragma STDC FENV_ACCESS ON
#endif

namespace {
void require(bool value, const char* message) {
  if (!value) throw std::runtime_error(message);
}
bool same(double a, double b) {
  return std::bit_cast<std::uint64_t>(a) == std::bit_cast<std::uint64_t>(b);
}
[[gnu::noinline]] double originalLoss(double u, double scale, double energy) {
  const double z = std::exp(-u);
  return std::abs(scale * energy * (z - 1.));
}
[[gnu::noinline]] double safeLoss(double u, double scale, double energy) {
  return std::abs(scale * energy * nodd::ttbar_safe_fatras::energyFractionMinusOne(u));
}
void compareParticle(const ActsFatras::Particle& first, const ActsFatras::Particle& second) {
  require(nodd::ttbar_safe_fatras::particleFailureState(first).dump()==nodd::ttbar_safe_fatras::particleFailureState(second).dump(), "Complete particle state changed");
  for (int i = 0; i < 4; ++i) {
    require(same(first.fourMomentum()[i], second.fourMomentum()[i]), "Particle momentum changed");
    if (i < 3) require(same(first.position()[i], second.position()[i]), "Particle position changed");
  }
  require(first.particleId() == second.particleId() && first.outcome() == second.outcome(), "Particle identity/outcome changed");
  require(same(first.time(), second.time()), "Particle time changed");
}
}  // namespace

[[gnu::noinline]] double originalTerminal(double up,double u2,double inv) {
  if(std::log(u2)*inv+std::log(up)<std::log(std::numeric_limits<double>::min()))return 0.;
  return up*std::pow(u2,inv);
}
[[gnu::noinline]] double guardedTerminal(double up,double u2,double inv) {
  return nodd::ttbar_safe_fatras::ZeroObservableGammaDistribution::finishSample(up,u2,inv);
}
int main() {
  require(std::fegetround() == FE_TONEAREST, "Test requires round-to-nearest");
  const std::vector<double> edges = {0., std::numeric_limits<double>::denorm_min(),
      std::numeric_limits<double>::min(), 1.e-300, 1.e-200, 1.e-100, 1.e-20,
      std::nextafter(0x1p-54, 0.), 0x1p-54, std::nextafter(0x1p-54, 1.),
      1.e-10, .1, 1., 36., 38.,
      std::nextafter(40., 0.), 40., std::nextafter(40., 100.), 41.,
      700., 708., 710., 744., 745., 800., 1.e4, 1.e100,
      std::numeric_limits<double>::max()};
  std::uint64_t comparisons = 0;
  std::vector<double> guardedInputs;
  auto compare = [&](double u) {
    require(same(std::exp(-u) - 1., nodd::ttbar_safe_fatras::energyFractionMinusOne(u)), "Rounded fraction changed");
    if ((0. <= u && u < 0x1p-54) || u > 40.) guardedInputs.push_back(u);
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
  for (double thickness : {1.e-8, 1.e-6, 1.e-4, .001, .01, .1, 1., 20., 80., 800.}) {
    Acts::MaterialSlab slab(material, 200. * thickness);
    for (std::uint64_t seed = 0; seed < 2000; ++seed) {
      std::mt19937_64 originalRng(seed), safeRng(seed);
      ActsFatras::Particle original(ActsFatras::Barcode{}, Acts::PdgParticle::eElectron);
      original.setAbsoluteMomentum(100.).setDirection(Acts::Vector3(.2, .3, 1.).normalized());
      auto guarded = original;
      const auto originalPhoton = nodd::safe_fatras::SafeBetheHeitler{}(originalRng, slab, original);
      std::feclearexcept(FE_ALL_EXCEPT);  // Old-path exceptions are intentional controls.
      ActsPlugins::FpeMonitor operatorMonitor;
      const auto guardedPhoton = nodd::ttbar_safe_fatras::SafeBetheHeitler{}(safeRng, slab, guarded);
      require(!operatorMonitor.result().encountered(ActsPlugins::FpeType::FLTUND) &&
              !operatorMonitor.result().encountered(ActsPlugins::FpeType::FLTINV) &&
              !operatorMonitor.result().encountered(ActsPlugins::FpeType::FLTDIV) &&
              !operatorMonitor.result().encountered(ActsPlugins::FpeType::FLTOVF), "Guarded full operator triggers native FPE monitor");
      require(originalRng == safeRng, "RNG engine state/order changed");
      compareParticle(original, guarded);
      compareParticle(originalPhoton[0], guardedPhoton[0]);
      ++operatorComparisons;
    }
  }

  // Actual source-mechanism fixture: final gamma product is normal, but
  // pow(.5,1023.5) is inexact subnormal. These are synthetic test values,
  // not recovered parameters from the failed production stack.
  std::feclearexcept(FE_ALL_EXCEPT);
  volatile double fixtureUp=4.,fixtureU2=.5,fixtureInv=1023.5;
  volatile double originalGamma=originalTerminal(fixtureUp,fixtureU2,fixtureInv);
  require(originalGamma>=std::numeric_limits<double>::min(),"Fixture final product is not normal");
  require(std::fetestexcept(FE_UNDERFLOW),"Original pow underflow positive control did not signal");
  const double expectedLoss=nodd::safe_fatras::energyFractionMinusOne(originalGamma);
  std::feclearexcept(FE_ALL_EXCEPT);
  volatile double guardedGamma=guardedTerminal(fixtureUp,fixtureU2,fixtureInv);
  require(same(expectedLoss,nodd::ttbar_safe_fatras::energyFractionMinusOne(guardedGamma)),"Observable fixture loss changed");
  require(guardedGamma==0. && !(std::fetestexcept(FE_UNDERFLOW|FE_INVALID|FE_DIVBYZERO|FE_OVERFLOW)),"Guarded fixture raises exception");
  {
    ActsPlugins::FpeMonitor monitor;
    volatile double guarded=guardedTerminal(fixtureUp,fixtureU2,fixtureInv);(void)guarded;
    require(!monitor.result().encountered(ActsPlugins::FpeType::FLTUND),"Guarded pow fixture triggers native FPE monitor");
  }
  using High=boost::multiprecision::number<boost::multiprecision::cpp_bin_float<200>>;
  std::uint64_t gammaComparisons=0;
  const double boundaryInv=512./std::log(2.);
  for(double up : {0.5,1.,4.,std::nextafter(0x1p256,0.),0x1p256,std::nextafter(0x1p256,std::numeric_limits<double>::infinity()),0x1p500}) {
    for(double u2 : {0x1p-64,.125,.5,std::nextafter(.5,1.),.9,std::nextafter(1.,0.)}) {
      for(double inv : {1.01,2.,100.,std::nextafter(boundaryInv,0.),boundaryInv,std::nextafter(boundaryInv,std::numeric_limits<double>::infinity()),1023.5,1.e4,1.e8}) {
        const double logPow=std::log(u2)*inv;
        const High exactLog=log(High(u2))*High(inv);
        require(abs(exactLog-High(logPow))<1,"Native log-power error exceeds conservative proof margin");
        const double oldGamma=originalTerminal(up,u2,inv),newGamma=guardedTerminal(up,u2,inv);
        require(same(nodd::safe_fatras::energyFractionMinusOne(oldGamma),nodd::ttbar_safe_fatras::energyFractionMinusOne(newGamma)),"Gamma guard changed rounded loss");
        if(!(up<=0x1p256 && logPow<-512.))require(same(oldGamma,newGamma),"Original gamma arithmetic outside guard changed");
        else require(log(High(up))+exactLog<High(-54)*log(High(2)),"Guarded real gamma is outside zero-loss region");
        ++gammaComparisons;
      }
    }
  }
  std::cout<<"PASS: "<<gammaComparisons<<" gamma boundary/high-precision controls, pow-underflow positive control and native FPE guard; ";

  // Both installed-libm underflows are positive controls. Volatile runtime
  // inputs and noinline wrappers prevent constant folding in the production
  // target, which deliberately has no FENV_ACCESS pragma or strict FP option.
  for (double value : {1.e-300, 800.}) {
    std::feclearexcept(FE_ALL_EXCEPT);
    volatile double input = value;
    volatile double original = originalLoss(input, 1., 123.25);
    (void)original;
    require(std::fetestexcept(FE_UNDERFLOW), "Original tiny/large underflow positive control did not signal");
  }
  std::feclearexcept(FE_ALL_EXCEPT);
  for (double input : guardedInputs) {
    std::feclearexcept(FE_ALL_EXCEPT);
    volatile double guarded = safeLoss(input, 1., 123.25);
    require(same(guarded, input > 40. ? 123.25 : 0.), "Guarded tiny/large loss changed");
    require(std::fetestexcept(FE_ALL_EXCEPT) == 0, "Guarded tiny/large path raised a hardware FP flag");
  }
  {
    ActsPlugins::FpeMonitor monitor;
    for (double input : guardedInputs) {
      volatile double guarded = safeLoss(input, 1., 123.25);
      (void)guarded;
    }
    require(!monitor.result().encountered(ActsPlugins::FpeType::FLTUND), "Guarded tiny/large path triggers native FPE monitor");
    require(!monitor.result().encountered(ActsPlugins::FpeType::FLTINV), "Guarded path triggers native invalid operation");
    require(!monitor.result().encountered(ActsPlugins::FpeType::FLTDIV), "Guarded path triggers native divide by zero");
    require(!monitor.result().encountered(ActsPlugins::FpeType::FLTOVF), "Guarded path triggers native overflow");
  }
  std::cout << "PASS: " << comparisons << " bitwise energy-loss comparisons, "
            << operatorComparisons << " exact parent/photon/RNG comparisons; "
            << guardedInputs.size() << " exponent-stratified guarded hardware/native FPE checks; tiny/large original-underflow positive controls; "
#ifdef NODD_TEST_STRICT_FP
            << "strict FP control\n";
#else
            << "native O2 production FP mode\n";
#endif
}
