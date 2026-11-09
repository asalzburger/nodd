// Copyright (C) 2026 CERN for the benefit of the ACTS project
// SPDX-License-Identifier: MPL-2.0
// PROTOTYPE diagnostics. Output contains event data: keep it local and ignored.
#include <edm4hep/EventHeaderCollection.h>
#include <edm4hep/SimCalorimeterHitCollection.h>
#include <podio/ROOTReader.h>
#include <nlohmann/json.hpp>

#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>

#include "Acts/Definitions/Units.hpp"
#include "ActsExamples/Calorimeter/CalorimeterDigitizationAlgorithm.hpp"
#include "ActsExamples/Calorimeter/EDM4hepCalorimeterInputConverter.hpp"

using namespace ActsExamples;
using nlohmann::json;

namespace {
class Access final : public IAlgorithm {
 public:
  Access() : IAlgorithm("ValidationAccess", Acts::getDefaultLogger("ValidationAccess", Acts::Logging::WARNING)) {
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
}

int main(int argc, char** argv) try {
  if (argc != 5) throw std::invalid_argument("Usage: nodd_silicon_validation INPUT.root CONFIG.json OUTPUT.jsonl BACKEND");
  if (std::filesystem::exists(argv[3])) throw std::invalid_argument("Output already exists");
  json config;
  std::ifstream(argv[2]) >> config;
  const auto collections=config.at("collections").get<std::vector<std::string>>();
  const bool saveCells=config.value("save_cells", false);
  podio::ROOTReader reader;
  reader.openFile(argv[1]);
  const auto events=reader.getEntries("events");
  std::ofstream output(argv[3]);
  if (!output) throw std::runtime_error("Cannot open diagnostics");
  for (std::size_t event=0; event<events; ++event) {
    json result={{"index",event},{"raw_GeV",0.0},{"modes",json::object()}};
    for (std::size_t collection=0; collection<collections.size(); ++collection) {
      const auto& name=collections[collection];
      auto frame=podio::Frame(reader.readEntry("events",event));
      const auto& headers=frame.get<edm4hep::EventHeaderCollection>("EventHeader");
      if (headers.size()!=1) throw std::runtime_error("Expected one EventHeader");
      json identity={headers[0].getRunNumber(),headers[0].getEventNumber()};
      if (collection && result["identity"]!=identity) throw std::runtime_error("Event identity changed");
      result["identity"]=identity;
      const auto& input=frame.get<edm4hep::SimCalorimeterHitCollection>(name);
      std::map<std::uint64_t,double> energies;
      double raw=0;
      for (const auto& hit:input) {
        if (energies.contains(hit.getCellID())) throw std::runtime_error("Duplicate input cell");
        double energy=0;
        for (const auto& contribution:hit.getContributions()) energy+=contribution.getEnergy();
        energies.emplace(hit.getCellID(),energy);
        raw+=hit.getEnergy();
      }
      result["raw_GeV"]=result["raw_GeV"].get<double>()+raw;
      for (const auto& mode:config.at("modes")) {
        const std::string label=mode.at("name");
        SiliconDigitizationConfig response;
        response.executable=argv[4];
        response.mipEnergy=config.at("mip_energy_GeV").get<double>()*Acts::UnitConstants::GeV;
        response.pairEnergyEv=mode.at("pair_energy_eV");
        response.noiseMip=mode.at("noise_MIP");
        response.thresholdMip=config.at("threshold_MIP");
        response.dynamicRangeMip=config.at("dynamic_range_MIP");
        response.seed=config.at("seed").get<std::uint64_t>()+collection;
        WhiteBoard board;
        AlgorithmContext context{0,event,board,0};
        Access access;
        access.frame(context,podio::Frame(reader.readEntry("events",event)));
        EDM4hepCalorimeterInputConverter::Config in;
        in.inputSimHits=name;
        in.outputDeposits="deposits";
        in.outputSources="sources";
        in.useHitPosition=true;
        EDM4hepCalorimeterInputConverter converter(in,Acts::Logging::WARNING);
        if (converter.execute(context)!=ProcessCode::SUCCESS) throw std::runtime_error("Input conversion failed");
        CalorimeterDigitizationAlgorithm::Config digi;
        digi.inputSimHits="deposits";
        digi.outputHits="digitized";
        digi.silicon=response;
        CalorimeterDigitizationAlgorithm algorithm(digi,Acts::Logging::WARNING);
        if (algorithm.execute(context)!=ProcessCode::SUCCESS) throw std::runtime_error("Digitization failed");
        double sum=0;
        for (const auto& hit:access.hits(context)) sum+=hit.energy/Acts::UnitConstants::GeV;
        auto& values=result["modes"][label];
        if (values.is_null()) values={{"energy_GeV",0.0},{"accepted_cells",0}};
        values["energy_GeV"]=values["energy_GeV"].get<double>()+sum;
        values["accepted_cells"]=values["accepted_cells"].get<std::size_t>()+access.hits(context).size();
        if (saveCells) {
          std::vector<double> deposits;
          for (const auto& [id,energy]:energies) deposits.push_back(energy*Acts::UnitConstants::GeV);
          const auto signedMip=runMarlinSilicon(response,deposits,event);
          json cells=json::array();
          std::size_t index=0, accepted=0;
          double checkSum=0;
          for (const auto& [id,energy]:energies) {
            const auto mip=signedMip.at(index++);
            cells.push_back({id,mip});
            if (mip>static_cast<float>(response.thresholdMip)) {
              ++accepted;
              checkSum+=mip*response.mipEnergy/Acts::UnitConstants::GeV;
            }
          }
          if (accepted!=access.hits(context).size() || std::abs(checkSum-sum)>1e-12*std::max(1.0,std::abs(sum)))
            throw std::runtime_error("Signed backend diagnostic disagrees with native algorithm");
          values["cells"][name]=std::move(cells);
        }
      }
    }
    output << result.dump() << '\n';
    if (!output) throw std::runtime_error("Cannot write diagnostics");
  }
  std::cout << "Native validation diagnostics: " << events << " events\n";
  return 0;
} catch (const std::exception& error) {
  std::cerr << error.what() << '\n';
  return 1;
}
