// PROTOTYPE exact finite-segment vacuum B and Coulomb-gauge A; SI throughout.
// No wire-radius softening: points on active source segments return NaN.
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <thread>
#include <vector>

extern "C" int field_evaluate(std::size_t point_count, const double* points,
    std::size_t segment_count, const double* endpoint_a, const double* endpoint_b,
    const double* currents, const std::int32_t* group_indices, int groups,
    int by_group, int want_b, int want_a, int thread_count,
    double* output_b, double* output_a) {
  struct Segment {
    double ax, ay, az, ux, uy, uz, length, current, tolerance;
    int group;
  };
  try {
    std::vector<Segment> segments;
    segments.reserve(segment_count);
    for (std::size_t i = 0; i < segment_count; ++i) {
      if (currents[i] == 0) continue;
      const double dx = endpoint_b[3*i]-endpoint_a[3*i];
      const double dy = endpoint_b[3*i+1]-endpoint_a[3*i+1];
      const double dz = endpoint_b[3*i+2]-endpoint_a[3*i+2];
      const double length = std::sqrt(dx*dx+dy*dy+dz*dz);
      segments.push_back({endpoint_a[3*i], endpoint_a[3*i+1], endpoint_a[3*i+2],
        dx/length, dy/length, dz/length, length, 1e-7*currents[i],
        32*std::numeric_limits<double>::epsilon()*std::max(1.0,length),
        by_group ? group_indices[i] : 0});
    }
    auto worker = [&](std::size_t begin, std::size_t end) {
      for (std::size_t i = begin; i < end; ++i) {
        const double px = points[3*i], py = points[3*i+1], pz = points[3*i+2];
        for (const auto& s : segments) {
          const double wx = px-s.ax, wy = py-s.ay, wz = pz-s.az;
          const double axial = wx*s.ux+wy*s.uy+wz*s.uz;
          const double rx = wx-axial*s.ux, ry = wy-axial*s.uy, rz = wz-axial*s.uz;
          const double rho2 = rx*rx+ry*ry+rz*rz;
          const double tail = axial-s.length;
          const double ra = std::sqrt(rho2+axial*axial);
          const double rb = std::sqrt(rho2+tail*tail);
          const bool on_axis = rho2 <= s.tolerance*s.tolerance;
          const bool singular = on_axis && axial >= -s.tolerance && tail <= s.tolerance;
          const std::size_t offset = 3*(i*groups+s.group);
          if (singular) {
            const double nan = std::numeric_limits<double>::quiet_NaN();
            if (want_b) output_b[offset] = output_b[offset+1] = output_b[offset+2] = nan;
            if (want_a) output_a[offset] = output_a[offset+1] = output_a[offset+2] = nan;
            continue;
          }
          if (want_b && !on_axis) {
            const double factor = s.current*(axial/ra-tail/rb)/rho2;
            output_b[offset] += factor*(s.uy*rz-s.uz*ry);
            output_b[offset+1] += factor*(s.uz*rx-s.ux*rz);
            output_b[offset+2] += factor*(s.ux*ry-s.uy*rx);
          }
          if (want_a) {
            // Rationalized ra+rb-L avoids cancellation near a filament.
            const double denominator = rho2/(ra+std::abs(axial))
                + rho2/(rb+std::abs(tail))
                + 2*std::max(-axial,0.0)+2*std::max(tail,0.0);
            const double integral = std::log1p(2*s.length/denominator);
            const double factor = s.current*integral;
            output_a[offset] += factor*s.ux;
            output_a[offset+1] += factor*s.uy;
            output_a[offset+2] += factor*s.uz;
          }
        }
      }
    };
    const std::size_t threads = std::min<std::size_t>(std::max(1,thread_count), point_count);
    if (threads <= 1) worker(0, point_count);
    else {
      std::vector<std::thread> workers;
      workers.reserve(threads);
      for (std::size_t thread = 0; thread < threads; ++thread) {
        workers.emplace_back(worker, point_count*thread/threads,
                             point_count*(thread+1)/threads);
      }
      for (auto& thread : workers) thread.join();
    }
    return 0;
  } catch (...) {
    return 1;
  }
}
