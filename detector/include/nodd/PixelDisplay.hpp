#pragma once
#include <DD4hep/Detector.h>
#include <DD4hep/Volumes.h>
#include <string>

namespace nodd {
// DD4hep's RGB matching may select a nearby palette entry. Use the explicitly
// configured standard ROOT index for the persisted TGeoVolume attributes.
inline void applyDisplay(dd4hep::Detector& detector, dd4hep::Volume volume,
                         const std::string& style) {
  volume.setVisAttributes(detector, style);
  const auto colour = detector.constant<int>("nodd_colour_" + style);
  volume->SetLineColor(colour);
  volume->SetFillColor(colour);
}
}  // namespace nodd
