#include <DD4hep/Volumes.h>
#include <TFile.h>
#include <TGeoManager.h>
#include <TGeoMaterial.h>
#include <TGeoNavigator.h>
#include <TH1D.h>
#include <TProfile.h>
#include <TTree.h>
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

// No detector simulation or geometry mutation: look up recorded step interiors.
void categorize(const char* input, const char* output, const char* diagnostics,
                long long limit = -1) {
  TFile source(input, "READ");
  auto* tree = source.Get<TTree>("material_tracks");
  if (!tree) throw std::runtime_error("Missing material_tracks");
  tree->SetBranchStatus("*", 0);
  float eta, phi, recordedX0, recordedL0;
  unsigned int event;
  std::vector<float> *x=nullptr, *y=nullptr, *z=nullptr, *dx=nullptr,
    *dy=nullptr, *dz=nullptr, *length=nullptr, *x0=nullptr, *l0=nullptr,
    *rho=nullptr;
  auto branch = [&](const char* name, auto address) {
    tree->SetBranchStatus(name, 1); tree->SetBranchAddress(name, address);
  };
  branch("event_id", &event); branch("v_eta", &eta); branch("v_phi", &phi);
  branch("t_X0", &recordedX0); branch("t_L0", &recordedL0);
  branch("mat_x", &x); branch("mat_y", &y); branch("mat_z", &z);
  branch("mat_dx", &dx); branch("mat_dy", &dy); branch("mat_dz", &dz);
  branch("mat_step_length", &length); branch("mat_X0", &x0);
  branch("mat_L0", &l0); branch("mat_rho", &rho);

  const std::array<std::string,8> names = {
    "beam_pipe_nonsensitive", "beam_pipe_sensitive", "pixel_nonsensitive",
    "pixel_sensitive", "short_strip_nonsensitive", "short_strip_sensitive",
    "long_strip_nonsensitive", "long_strip_sensitive"};
  TFile target(output, "RECREATE");
  TTree tracks("categorized_tracks", "Per-geantino material in each component");
  tracks.SetDirectory(nullptr);
  double totals[2][8] = {};
  double ambiguous[2] = {};
  tracks.Branch("rounding_ambiguous_X0", &ambiguous[0]);
  tracks.Branch("rounding_ambiguous_L0", &ambiguous[1]);
  tracks.Branch("event_id", &event);
  tracks.Branch("eta", &eta); tracks.Branch("phi", &phi);
  tracks.Branch("recorded_X0", &recordedX0);
  tracks.Branch("recorded_L0", &recordedL0);
  const std::array<std::string, 2> units = {"X0", "L0"};
  for (int q=0; q<2; ++q)
    for (int c=0; c<8; ++c)
      tracks.Branch((names[c]+"_"+units[q]).c_str(), &totals[q][c]);

  const std::array<std::string,3> axes = {"eta", "abs_eta", "phi"};
  const std::array<int,3> nbins = {90,45,72};
  const std::array<double,3> lo = {-4.5,0,-M_PI}, hi = {4.5,4.5,M_PI};
  std::unique_ptr<TProfile> profiles[3][2][9];
  std::unique_ptr<TH1D> occupancy[3];
  for (int a=0; a<3; ++a) {
    occupancy[a] = std::make_unique<TH1D>(("tracks_"+axes[a]).c_str(), "", nbins[a],lo[a],hi[a]);
    occupancy[a]->SetDirectory(nullptr);
    for (int q=0; q<2; ++q)
      for (int c=0; c<9; ++c) {
        auto name = (c<8 ? names[c] : "total")+"_"+units[q]+"_vs_"+axes[a];
        profiles[a][q][c] = std::make_unique<TProfile>(name.c_str(), "", nbins[a],lo[a],hi[a]);
        profiles[a][q][c]->SetDirectory(nullptr);
        profiles[a][q][c]->GetXaxis()->SetTitle(axes[a].c_str());
      }
  }

  auto* navigator = gGeoManager->GetCurrentNavigator();
  // Acts mass density uses natural energy units. Calibrate only this unit
  // conversion with the beam-pipe Be entry, and then verify all step densities.
  double densityUnit = 0;
  long long nsteps=0, missing=0, densityMismatch=0, fallback=0, boundaryRescue=0, sensitivityAmbiguous=0;
  std::array<long long,8> counts{};
  std::map<std::string,long long> materials;
  std::unordered_map<TGeoVolume*,int> categories;
  double maxClosure[2] = {}, globalSum[2][8] = {};
  std::ofstream log(diagnostics);
  log << "track,step,issue,x_mm,y_mm,z_mm,path,recorded_density,geometry_density\n";
  auto ntracks = tree->GetEntries();
  if (limit>=0) ntracks=std::min(ntracks,limit);
  for (long long i=0; i<ntracks; ++i) {
    tree->GetEntry(i);
    for (auto& quantity : totals) std::fill(std::begin(quantity), std::end(quantity), 0.);
    ambiguous[0]=ambiguous[1]=0.;
    const auto n = x->size();
    for (auto* v : {y,z,dx,dy,dz,length,x0,l0,rho})
      if (v->size()!=n) throw std::runtime_error("Inconsistent step vector lengths");
    for (size_t j=0; j<n; ++j) {
      ++nsteps;
      const double len=length->at(j);
      if (!(len>=0 && std::isfinite(len) && x0->at(j)>0 && l0->at(j)>0))
        throw std::runtime_error("Invalid material step");
      auto find = [&](double fraction) {
        // DD4hep/TGeo lengths are cm; recorder lengths/positions are mm.
        return navigator->FindNode(.1*(x->at(j)+fraction*len*dx->at(j)),
                                   .1*(y->at(j)+fraction*len*dy->at(j)),
                                   .1*(z->at(j)+fraction*len*dz->at(j)));
      };
      auto* node=find(.5);
      if (!densityUnit && node && std::string(node->GetVolume()->GetMaterial()->GetName())=="Beryllium")
        densityUnit=rho->at(j)/node->GetVolume()->GetMaterial()->GetDensity();
      auto matches = [&](TGeoNode* candidate) {
        if (!candidate || !densityUnit) return false;
        double expected=candidate->GetVolume()->GetMaterial()->GetDensity()*densityUnit;
        return std::abs(rho->at(j)-expected)<=5e-6*std::max(expected,static_cast<double>(rho->at(j)));
      };
      if (!matches(node)) {
        // Thin slivers can lose their midpoint in float32. Require a material
        // match at another strict interior point rather than guessing by radius.
        for (double f : {.25,.75,.1,.9,.01,.99}) {
          node=find(f);
          if (matches(node)) { ++fallback; break; }
        }
      }
      if (!matches(node)) {
        // The true pre-step coordinate is within half an ulp of the stored
        // float32 coordinate. Very short steps and tangential tube chords can
        // be thinner than that uncertainty. Search only this rounding cell,
        // and accept a rescue only if ALL density-matching candidates agree
        // on subdetector and sensitivity. Never enlarge the rounding cell.
        const std::array<float,3> origin={x->at(j),y->at(j),z->at(j)};
        const std::array<float,3> direction={dx->at(j),dy->at(j),dz->at(j)};
        std::array<double,3> centre{}, halfUlp{};
        for (int k=0;k<3;++k) {
          centre[k]=origin[k]+.5*len*direction[k];
          halfUlp[k]=.5*std::max(
            std::abs(double(std::nextafter(origin[k],INFINITY))-origin[k]),
            std::abs(double(std::nextafter(origin[k],-INFINITY))-origin[k]));
        }
        std::set<int> possible;
        std::map<int,std::array<double,3>> candidateByCategory;
        std::array<double,3> chosen{};
        for (double ox:{-1.,-.5,0.,.5,1.})
          for (double oy:{-1.,-.5,0.,.5,1.})
            for (double oz:{-1.,-.5,0.,.5,1.}) {
              std::array<double,3> candidate={centre[0]+ox*halfUlp[0],centre[1]+oy*halfUlp[1],centre[2]+oz*halfUlp[2]};
              auto* found=navigator->FindNode(.1*candidate[0],.1*candidate[1],.1*candidate[2]);
              if (!matches(found)) continue;
              std::string path=navigator->GetPath();
              int subdet=-1;
              if (path.find("/BeamPipe_")!=std::string::npos) subdet=0;
              else if (path.find("/Pixel")!=std::string::npos) subdet=1;
              else if (path.find("/ShortStrip")!=std::string::npos) subdet=2;
              else if (path.find("/LongStrip")!=std::string::npos) subdet=3;
              if (subdet>=0) {
                int c=2*subdet+int(dd4hep::Volume(found->GetVolume()).isSensitive());
                possible.insert(c);
                candidateByCategory[c]=candidate;
                chosen=candidate;
              }
            }
        std::string resolution="float32_boundary_resolved";
        if (possible.size()>1) {
          // A nanometre-scale silicon step can fall on an active/guard edge.
          // The saved floats then cannot resolve sensitivity. Keep its material
          // in the unanimously identified subdetector, allocate non-sensitive,
          // and retain the FULL budget as a sensitivity-allocation bound.
          if (possible.size()!=2 || *possible.begin()/2!=*possible.rbegin()/2)
            throw std::runtime_error("Ambiguous subdetector inside float32 rounding cell");
          chosen=candidateByCategory.at(*possible.begin());
          ++sensitivityAmbiguous;
          ambiguous[0]+=len/x0->at(j); ambiguous[1]+=len/l0->at(j);
          resolution="float32_sensitivity_lower_bound";
        }
        if (!possible.empty()) {
          node=navigator->FindNode(.1*chosen[0],.1*chosen[1],.1*chosen[2]);
          ++boundaryRescue;
          log<<std::setprecision(17)<<i<<','<<j<<','<<resolution<<','<<chosen[0]<<','<<chosen[1]<<','<<chosen[2]<<','
             <<navigator->GetPath()<<','<<rho->at(j)<<','<<node->GetVolume()->GetMaterial()->GetDensity()<<'\n';
        } else node=find(.5);
      }
      if (!node) { ++missing; continue; }
      auto* volume=node->GetVolume();
      if (!matches(node)) {
        ++densityMismatch;
        if (densityMismatch<101)
          log<<i<<','<<j<<",density,"<<x->at(j)<<','<<y->at(j)<<','<<z->at(j)<<','
             <<navigator->GetPath()<<','<<rho->at(j)<<','<<volume->GetMaterial()->GetDensity()<<'\n';
      }
      int category=-1;
      auto cached=categories.find(volume);
      if (cached!=categories.end()) category=cached->second;
      else {
        const std::string path=navigator->GetPath();
        int subdet=-1;
        if (path.find("/BeamPipe_")!=std::string::npos) subdet=0;
        else if (path.find("/Pixel")!=std::string::npos) subdet=1;
        else if (path.find("/ShortStrip")!=std::string::npos) subdet=2;
        else if (path.find("/LongStrip")!=std::string::npos) subdet=3;
        if (subdet>=0) category=2*subdet+int(dd4hep::Volume(volume).isSensitive());
        categories[volume]=category;
      }
      if (category<0) {
        ++missing;
        if (missing<101)
          log<<i<<','<<j<<",unassigned,"<<x->at(j)<<','<<y->at(j)<<','<<z->at(j)<<','
             <<navigator->GetPath()<<','<<rho->at(j)<<','<<volume->GetMaterial()->GetDensity()<<'\n';
        continue;
      }
      ++counts[category];
      ++materials[names[category]+":"+volume->GetMaterial()->GetName()];
      totals[0][category] += len/x0->at(j);
      totals[1][category] += len/l0->at(j);
    }
    std::array<double,3> coordinates={eta,std::abs(eta),phi};
    double sum[2]{};
    for (int q=0; q<2; ++q) {
      for (int c=0; c<8; ++c) {sum[q]+=totals[q][c]; globalSum[q][c]+=totals[q][c];}
      maxClosure[q]=std::max(maxClosure[q],std::abs(sum[q]-(q==0?recordedX0:recordedL0)));
    }
    for (int a=0; a<3; ++a) {
      occupancy[a]->Fill(coordinates[a]);
      for (int q=0; q<2; ++q) {
        for (int c=0; c<8; ++c) profiles[a][q][c]->Fill(coordinates[a],totals[q][c]);
        profiles[a][q][8]->Fill(coordinates[a],sum[q]);
      }
    }
    tracks.Fill();
    if ((i+1)%10000==0) std::cout<<"PROGRESS "<<i+1<<" tracks / "<<nsteps<<" steps"<<std::endl;
  }
  target.cd(); tracks.Write();
  for (int a=0; a<3; ++a) {
    occupancy[a]->Write();
    for (int q=0; q<2; ++q) for (int c=0; c<9; ++c) profiles[a][q][c]->Write();
  }
  // Write the numerical report through ROOT's JSON-independent C++ stream.
  std::ofstream report(std::string(output)+".json");
  report<<std::setprecision(17)<<"{\n\"tracks\":"<<ntracks<<",\n\"steps\":"<<nsteps
        <<",\n\"unassigned_steps\":"<<missing<<",\n\"density_mismatches\":"<<densityMismatch
        <<",\n\"interior_fallback_steps\":"<<fallback<<",\n\"density_unit\":"<<densityUnit
        <<",\n\"float32_boundary_rescues\":"<<boundaryRescue
        <<",\n\"sensitivity_ambiguous_steps\":"<<sensitivityAmbiguous
        <<",\n\"max_track_closure_absolute\":{\"X0\":"<<maxClosure[0]<<",\"L0\":"<<maxClosure[1]<<"},\n\"components\":{\n";
  for (int c=0; c<8; ++c)
    report<<'"'<<names[c]<<"\":{\"steps\":"<<counts[c]<<",\"mean_X0\":"<<globalSum[0][c]/ntracks
          <<",\"mean_L0\":"<<globalSum[1][c]/ntracks<<"}"<<(c==7?"\n":",\n");
  report<<"},\n\"materials\":{\n";
  size_t k=0;
  for (auto& [name,count]:materials) report<<'"'<<name<<"\":"<<count<<(++k==materials.size()?"\n":",\n");
  report<<"}}\n";
  target.Close();
  std::cout<<"DONE "<<ntracks<<" tracks, "<<nsteps<<" steps, "<<missing<<" unassigned, "
           <<densityMismatch<<" material mismatches"<<std::endl;
}
