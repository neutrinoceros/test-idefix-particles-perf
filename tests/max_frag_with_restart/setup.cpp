#include <string>
#include "idefix.hpp"
#include "setup.hpp"

real PM; // particle mass
int perCell {-1};

// Initialisation routine. Can be used to allocate
// Arrays or variables which are used later on
Setup::Setup(Input &input, Grid &grid, DataBlock &data, Output &output) {
  PM = input.Get<real>("Setup", "mass", 0);
  if(input.Get<std::string>("Particles", "count", 0).compare("per_cell")!=0) {
    IDEFIX_ERROR("this setup requires initial particle count to use 'per_cell' mode");
  }
  perCell = input.Get<int>("Particles", "count", 1);
}
void Setup::InitFlow(DataBlock &data) {
  DataBlockHost d(data);

  // init flow
  for(int k = 0; k < d.np_tot[KDIR] ; k++) {
    for(int j = 0; j < d.np_tot[JDIR] ; j++) {
      for(int i = 0; i < d.np_tot[IDIR] ; i++) {
        d.Vc(RHO,k,j,i) = ONE_F;
        d.Vc(VX1,k,j,i) = ZERO_F;
        d.Vc(VX2,k,j,i) = ZERO_F;
        d.Vc(VX3,k,j,i) = ZERO_F;
      }
    }
  }


  // uniformly distribute particles at cell centers
  const int ighost = d.nghost[IDIR];
  const int jghost = d.nghost[JDIR];
  const int kghost = d.nghost[KDIR];
  int idx = 0;
  for(int k = 0; k < d.np_int[KDIR] ; k++) {
    for(int j = 0; j < d.np_int[JDIR] ; j++) {
      for(int i = 0; i < d.np_int[IDIR] ; i++) {
        for(int p = 0; p < perCell ; p++) {
          d.Ps(PX1,idx) = d.x[IDIR](ighost+i);
          d.Ps(PX2,idx) = d.x[JDIR](jghost+j);
          d.Ps(PX3,idx) = d.x[KDIR](kghost+k);
          d.Ps(PVX1,idx) = ZERO_F;
          d.Ps(PVX2,idx) = ZERO_F;
          d.Ps(PVX3,idx) = ZERO_F;

          d.Ps(PMASS,idx) = PM;
          ++idx;
        }

        d.Ps(PMASS,k) = PM;
        // kill one-out-of two particles
        if(i%2==0) d.PisActive(k) = false;
      }
    }
  }
  d.SyncToDevice();
}

// Analyse data to produce an output
void MakeAnalysis(DataBlock & data) {

}
