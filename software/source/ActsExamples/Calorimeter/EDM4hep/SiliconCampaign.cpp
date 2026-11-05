// Copyright (C) 2026 CERN for the benefit of the ACTS project
// SPDX-License-Identifier: MPL-2.0
// PROTOTYPE: sparse signal-cell characterization, no shower calibration.
#include <podio/ROOTReader.h>
#include <edm4hep/SimCalorimeterHitCollection.h>
#include <nlohmann/json.hpp>

#include <cmath>
#include <fstream>
#include <iostream>
#include <stdexcept>

#include "Acts/Definitions/Units.hpp"
#include "ActsExamples/Calorimeter/CalorimeterDigitizationAlgorithm.hpp"
#include "ActsExamples/Calorimeter/EDM4hepCalorimeterInputConverter.hpp"

using namespace ActsExamples;
using nlohmann::json;

namespace {
class Access final : public IAlgorithm {
 public:
  Access() : IAlgorithm("CampaignAccess", Acts::getDefaultLogger("CampaignAccess", Acts::Logging::WARNING)) {
    m_frame.initialize("events");
    m_hits.initialize("digitized");
  }
  ProcessCode execute(const AlgorithmContext&) const override { return ProcessCode::SUCCESS; }
  void frame(const AlgorithmContext& context, podio::Frame value) { m_frame(context, std::move(value)); }
  const auto& hits(const AlgorithmContext& context) { return m_hits(context); }
 private:
  WriteDataHandle<podio::Frame> m_frame{this, "Frame"};
  ReadDataHandle<ActsCalorimeter::CalorimeterHitContainer> m_hits{this, "Hits"};
};

struct Histogram {
  double low, high;
  std::vector<std::uint64_t> counts;
  std::uint64_t underflow = 0, overflow = 0;
  Histogram(double a, double b, std::size_t bins) : low(a), high(b), counts(bins) {}
  void fill(double value) {
    if (!std::isfinite(value)) throw std::runtime_error("Nonfinite observable");
    if (value < low) ++underflow;
    else if (value >= high) ++overflow;
    else ++counts.at(static_cast<std::size_t>((value-low)/(high-low)*counts.size()));
  }
  json data(const std::string& unit) const {
    std::vector<double> edges;
    for (std::size_t i=0; i<=counts.size(); ++i) edges.push_back(low+(high-low)*i/counts.size());
    return {{"edges",edges},{"counts",counts},{"underflow",underflow},{"overflow",overflow},
            {"unit",unit},{"normalization","counts; all input events retained, including zero response"}};
  }
};

struct Moments {
  std::uint64_t n = 0;
  double x=0, y=0, xx=0, yy=0, xy=0;
  void fill(double a, double b) { ++n; x+=a; y+=b; xx+=a*a; yy+=b*b; xy+=a*b; }
  json data() const { return {{"n",n},{"sum_visible",x},{"sum_digitized",y},
      {"sum_visible_squared",xx},{"sum_digitized_squared",yy},{"sum_product",xy},
      {"unit","GeV; squared and product quantities GeV^2"}}; }
};
}  // namespace

int main(int argc, char** argv) try {
  if (argc != 5) throw std::invalid_argument("Usage: nodd_silicon_campaign INPUT.root CONFIG.json OUTPUT.json BACKEND");
  json config; std::ifstream(argv[2]) >> config;
  SiliconDigitizationConfig silicon;
  silicon.executable=argv[4];
  silicon.mipEnergy=config.at("mip_energy_GeV").get<double>()*Acts::UnitConstants::GeV;
  silicon.noiseMip=config.at("noise_MIP");
  silicon.thresholdMip=config.at("threshold_MIP");
  silicon.dynamicRangeMip=config.at("dynamic_range_MIP");
  silicon.seed=config.at("seed");
  const double beam=config.at("beam_energy_GeV");
  if (!(beam>0) || !std::isfinite(beam)) throw std::invalid_argument("Invalid beam energy");
  const auto collections=config.at("collections").get<std::vector<std::string>>();
  const std::size_t skip=config.value("skip_events",std::size_t{0});
  podio::ROOTReader reader; reader.openFile(argv[1]);
  const auto events=reader.getEntries("events");
  if (skip>=events) throw std::invalid_argument("Empty event selection");
  Histogram visible(0,.10,200), digitized(0,.10,200), simCell(0,.0005,200), digiCell(0,5,200);
  Moments moments;
  std::uint64_t empty=0;
  for (std::size_t event=skip; event<events; ++event) {
    double simSum=0, digiSum=0;
    for (const auto& name: collections) {
      podio::Frame frame=reader.readEntry("events",event);
      const auto& input=frame.get<edm4hep::SimCalorimeterHitCollection>(name);
      for (const auto& hit:input) { simSum+=hit.getEnergy(); simCell.fill(hit.getEnergy()); }
      WhiteBoard board;
      AlgorithmContext context{0,event,board,0};
      Access access; access.frame(context,std::move(frame));
      EDM4hepCalorimeterInputConverter::Config in;
      in.inputSimHits=name; in.outputDeposits="deposits"; in.outputSources="sources"; in.useHitPosition=true;
      EDM4hepCalorimeterInputConverter converter(in,Acts::Logging::WARNING);
      if (converter.execute(context)!=ProcessCode::SUCCESS) throw std::runtime_error("Input conversion failed");
      auto response=silicon;
      // Separate deterministic streams for barrel/endcap collections.
      response.seed+=(&name-&collections.front());
      CalorimeterDigitizationAlgorithm::Config digi;
      digi.inputSimHits="deposits"; digi.outputHits="digitized"; digi.silicon=response;
      CalorimeterDigitizationAlgorithm algorithm(digi,Acts::Logging::WARNING);
      if (algorithm.execute(context)!=ProcessCode::SUCCESS) throw std::runtime_error("Digitization failed");
      for (const auto& hit:access.hits(context)) {
        digiSum+=hit.energy/Acts::UnitConstants::GeV;
        digiCell.fill(hit.energy/silicon.mipEnergy);
      }
    }
    if (digiSum==0) ++empty;
    moments.fill(simSum,digiSum); visible.fill(simSum/beam); digitized.fill(digiSum/beam);
  }
  json result={{"status","PROTOTYPE characterization"},{"configuration",config},
      {"input_events",events},{"selected_events",events-skip},{"zero_digitized_events",empty},
      {"moments",moments.data()},{"visible_fraction",visible.data("1")},
      {"digitized_fraction",digitized.data("1")},{"sim_cell_energy",simCell.data("GeV")},
      {"digitized_cell_energy",digiCell.data("MIP")},
      {"limitations",{"Sparse signal cells only; full-detector empty-channel noise not simulated.",
       "Digitized energy is deposit-equivalent; no beam/shower calibration.",
       "Visible fraction is silicon deposit / beam energy, not active-plus-passive sampling fraction.",
       "Original response kernel is reused; original full Marlin processor comparison remains separate."}}};
  std::ofstream output(argv[3]); output << result.dump(2) << '\n';
  if (!output) throw std::runtime_error("Cannot write summary");
  std::cout << "Summarized " << events-skip << " events\n";
  return 0;
} catch (const std::exception& error) {
  std::cerr << error.what() << '\n'; return 1;
}
