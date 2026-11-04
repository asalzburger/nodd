// A separate image proves that ordinary public API calls reach the sentinel.
#include <G4ProductionCutsTable.hh>
#include <vector>

extern "C" void materialProfileClientEnergyCutVector(void* table, size_t count) {
  static_cast<G4ProductionCutsTable*>(table)->SetEnergyCutVector(
      std::vector<double>(count,0.001),0);
}
