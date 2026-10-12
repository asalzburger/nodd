// Reusable passive parts for DES015. All dimensions come from unit-bearing XML.
#pragma once
#include <DD4hep/Detector.h>
#include <DD4hep/Volumes.h>
#include <XML/XMLElements.h>
namespace nodd {
dd4hep::Volume buildEndcapPart(dd4hep::Detector&, dd4hep::xml::Handle_t);
void placeEndcapParts(dd4hep::Detector&, dd4hep::Volume, dd4hep::xml::Handle_t);
}
