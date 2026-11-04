// Regression for precision searches crossing a float32 binade boundary.
#include "rounding_cell.h"
#include <cassert>
#include <cmath>
#include <initializer_list>
#include <limits>

int main() {
  const auto positive = floatRoundingCell(128.f);
  assert(positive.lowerHalfWidth == std::ldexp(1., -18));
  assert(positive.upperHalfWidth == std::ldexp(1., -17));
  const auto negative = floatRoundingCell(-128.f);
  assert(negative.lowerHalfWidth == std::ldexp(1., -17));
  assert(negative.upperHalfWidth == std::ldexp(1., -18));
  const auto ordinary = floatRoundingCell(127.5f);
  assert(ordinary.lowerHalfWidth == std::ldexp(1., -18));
  assert(ordinary.upperHalfWidth == std::ldexp(1., -18));
  const auto zero = floatRoundingCell(0.f);
  assert(zero.lowerHalfWidth == std::ldexp(1., -150));
  assert(zero.upperHalfWidth == std::ldexp(1., -150));
  for (double fraction : {-1., -.5, 0., .5, 1.}) {
    const double point = 128. + positive.offset(fraction);
    assert(point >= 128. - std::ldexp(1., -18));
    assert(point <= 128. + std::ldexp(1., -17));
  }
  bool rejected = false;
  try { floatRoundingCell(std::numeric_limits<float>::infinity()); }
  catch (const std::invalid_argument&) { rejected = true; }
  assert(rejected);
}
