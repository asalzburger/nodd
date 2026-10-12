#pragma once
#include <DD4hep/Detector.h>
#include <DD4hep/Volumes.h>
#include <XML/XMLElements.h>
namespace nodd {
// A material-normalized annular sector; all dimensions and material from XML.
dd4hep::Volume buildServiceSector(dd4hep::Detector&, dd4hep::xml::Handle_t);
}
