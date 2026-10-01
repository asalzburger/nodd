// Reusable DD4hep components for the isolated DES-012 pixel-barrel prototype.
#pragma once

#include <DD4hep/DetElement.h>
#include <DD4hep/Detector.h>
#include <DD4hep/Volumes.h>
#include <XML/XMLElements.h>

#include <string>
#include <utility>
#include <vector>

namespace nodd {

// Module frames are (u,v) in the sensor plane, with +w toward the support.
// Stave frames use (u=tangent, v=beam, w=outward radial).
// XML lengths are evaluated by DD4hep and must carry explicit units.
struct ModuleBuild {
  dd4hep::Assembly volume;
  dd4hep::PlacedVolume substrate;
  std::vector<std::pair<int, dd4hep::PlacedVolume>> patches;
};

// module: name; sensor: u,v,width,length,thickness,material,vis;
// sensor/patch: id,u,v,width,length (sensor centre is w=0);
// passive and die: name,u,v,w,width,length,thickness,material,vis.
ModuleBuild buildModule(dd4hep::Detector& detector, dd4hep::xml::Handle_t xml,
                        dd4hep::SensitiveDetector sensitive);

// stave: name,length; slab: name,width,thickness,w,center_y,material,vis;
// core: same slab fields plus tube_outer,tube_inner,tube_offset,
// tube_material,coolant_material. A foam box contains two solid-cylinder Ti
// daughters, each with a CO2 daughter; child volumes replace parent material.
dd4hep::Assembly buildStave(dd4hep::Detector& detector,
                           dd4hep::xml::Handle_t xml);

// ring: name,rmin,rmax,length,material,vis; tube axis is global beam z.
dd4hep::Volume buildRing(dd4hep::Detector& detector, dd4hep::xml::Handle_t xml);

// foot: name,width,length,back_radius,outer_radius,material,vis.
// Return shape is centred at (back_radius+outer_radius)/2 along local w;
// the caller places that centre at the corresponding global radial position.
// Its outer surface is clipped to the coaxial cylinder outer_radius.
dd4hep::Volume buildFoot(dd4hep::Detector& detector, dd4hep::xml::Handle_t xml);

}  // namespace nodd
