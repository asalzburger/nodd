// Visualization only: coordinates arrive in metres from native ACTS faces.
#include "Acts/Visualization/ObjVisualization3D.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

int main(int argc, char** argv) {
  try {
    if (argc != 3) {
      throw std::runtime_error("usage: nodd-muon-obj OBJECTS.txt OUTPUT.obj");
    }
    std::ifstream input(argv[1]);
    std::size_t count = 0;
    if (!(input >> count) || count == 0) {
      throw std::runtime_error("missing objects");
    }
    Acts::ObjVisualization3D writer(17, 1.);
    std::set<std::string> names;
    for (std::size_t i = 0; i < count; ++i) {
      std::string name;
      int red = 0, green = 0, blue = 0;
      std::size_t faces = 0;
      if (!(input >> name >> red >> green >> blue >> faces) || faces == 0 ||
          red < 0 || green < 0 || blue < 0 || red > 255 || green > 255 ||
          blue > 255 || !names.insert(name).second) {
        throw std::runtime_error("invalid object identity/color/count");
      }
      writer.object(name);
      for (std::size_t j = 0; j < faces; ++j) {
        std::size_t size = 0;
        if (!(input >> size) || size < 3 || size > 16) {
          throw std::runtime_error("invalid polygon size");
        }
        std::vector<Acts::Vector3> vertices(size);
        for (auto& v : vertices) {
          if (!(input >> v.x() >> v.y() >> v.z()) || !v.allFinite()) {
            throw std::runtime_error("invalid polygon vertex");
          }
        }
        writer.face(vertices, {red, green, blue});
      }
    }
    std::string extra;
    if (input >> extra) {
      throw std::runtime_error("trailing input");
    }
    std::filesystem::path path(argv[2]);
    auto material = path;
    material.replace_extension(".mtl");
    std::ofstream obj(path), mtl(material);
    if (!obj || !mtl) {
      throw std::runtime_error("cannot open OBJ/MTL output");
    }
    obj << "# DES040 current chamber envelopes and toroid warm envelopes\n"
        << "# Coordinates: metres; right-handed Cartesian axes; beam along z\n"
        << "mtllib " << material.filename().string() << '\n';
    writer.write(obj, mtl);
    obj.flush();
    mtl.flush();
    if (!obj || !mtl) {
      throw std::runtime_error("OBJ/MTL write failed");
    }
    std::cout << "ACTS ObjVisualization3D wrote " << count << " objects\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
