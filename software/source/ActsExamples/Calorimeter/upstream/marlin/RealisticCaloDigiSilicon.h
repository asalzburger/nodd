// SPDX-License-Identifier: GPL-3.0-only
// Standalone interface adapter for MarlinReco255967eb energy methods.
// This header deliberately replaces framework registration, not physics.
#pragma once
#include <map>
#include <string>
#include <utility>

namespace lcio {}
namespace marlin {
class Processor {
public:
  explicit Processor(const std::string & = "") {}
  virtual ~Processor() = default;
  template <typename T>
  void registerProcessorParameter(const std::string &, const std::string &,
                                  T &target, T initial) {
    target = initial;
  }
  std::string _description;
};
} // namespace marlin

class RealisticCaloDigi : virtual public marlin::Processor {
public:
  RealisticCaloDigi() : marlin::Processor("RealisticCaloDigi") {}
  virtual ~RealisticCaloDigi() = default;
  enum { MIP, GEVDEP, NPE };
  virtual float EnergyDigi(float energy, int id0, int id1);
  virtual float digitiseDetectorEnergy(float energy) const = 0;
  virtual float convertEnergy(float energy, int unit) const = 0;
  float _calib_mip = 0;
  float _misCalib_uncorrel = 0;
  bool _misCalib_uncorrel_keep = false;
  float _misCalib_correl = 0;
  float _event_correl_miscalib = 0;
  float _elec_rangeMip = 0;
  float _elec_noiseMip = 0;
  float _deadCell_fraction = 0;
  bool _deadCell_keep = false;
  std::map<std::pair<int, int>, float> _cell_miscalibs;
  std::map<std::pair<int, int>, bool> _cell_dead;
};

class RealisticCaloDigiSilicon : public RealisticCaloDigi {
public:
  RealisticCaloDigiSilicon();
  float convertEnergy(float energy, int unit) const override;
  float digitiseDetectorEnergy(float energy) const override;
  float _ehEnergy = 0;
};
