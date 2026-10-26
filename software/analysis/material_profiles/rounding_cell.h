#pragma once

#include <cmath>
#include <limits>
#include <stdexcept>

struct FloatRoundingCell {
  double lowerHalfWidth;
  double upperHalfWidth;

  double offset(double fraction) const {
    return fraction * (fraction < 0 ? lowerHalfWidth : upperHalfWidth);
  }
};

inline FloatRoundingCell floatRoundingCell(float value) {
  if (!std::isfinite(value)) throw std::invalid_argument("Nonfinite coordinate");
  const auto infinity = std::numeric_limits<float>::infinity();
  return {
    .5 * (double(value) - double(std::nextafter(value, -infinity))),
    .5 * (double(std::nextafter(value, infinity)) - double(value))
  };
}
