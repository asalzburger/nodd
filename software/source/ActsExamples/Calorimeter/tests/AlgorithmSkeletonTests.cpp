// Copyright (C) 2026 CERN for the benefit of the ACTS project
// SPDX-License-Identifier: MPL-2.0
#include <boost/test/unit_test.hpp>
#include <stdexcept>

#include "ActsExamples/Calorimeter/CalorimeterClusteringAlgorithm.hpp"
#include "ActsExamples/Calorimeter/CalorimeterDigitizationAlgorithm.hpp"
#include "ActsTests/CommonHelpers/WhiteBoardUtilities.hpp"

using namespace ActsExamples;

BOOST_AUTO_TEST_CASE(RejectInvalidCollectionNames) {
  BOOST_CHECK_THROW(CalorimeterDigitizationAlgorithm({"", "hits"}),
                    std::invalid_argument);
  BOOST_CHECK_THROW(CalorimeterDigitizationAlgorithm({"same", "same"}),
                    std::invalid_argument);
  BOOST_CHECK_THROW(CalorimeterClusteringAlgorithm({"hits", ""}),
                    std::invalid_argument);
  BOOST_CHECK_THROW(CalorimeterClusteringAlgorithm({"same", "same"}),
                    std::invalid_argument);
}

BOOST_AUTO_TEST_CASE(UnimplementedStagesCannotProduceSuccessfulEmptyEvents) {
  WhiteBoard board;
  AlgorithmContext context{0, 0, board, 0};
  ActsTests::addToWhiteBoard(
      "deposits", ActsCalorimeter::SimCalorimeterHitContainer{}, board);
  ActsTests::addToWhiteBoard("hits", ActsCalorimeter::CalorimeterHitContainer{},
                             board);
  CalorimeterDigitizationAlgorithm digitization({"deposits", "digitized"});
  CalorimeterClusteringAlgorithm clustering({"hits", "clusters"});
  BOOST_CHECK_THROW(digitization.execute(context), std::logic_error);
  BOOST_CHECK_THROW(clustering.execute(context), std::logic_error);
  BOOST_CHECK(!board.exists("digitized"));
  BOOST_CHECK(!board.exists("clusters"));
  BOOST_CHECK_EQUAL(digitization.config().inputSimHits, "deposits");
  BOOST_CHECK_EQUAL(clustering.config().outputClusters, "clusters");
}
