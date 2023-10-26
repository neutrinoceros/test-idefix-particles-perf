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


  // randomized initial positions and velocities
  for(int k = 0; k < d.PactiveCount; k++) {
    d.Ps(PX1,k) = d.xbeg[IDIR] + idfx::randm() * (d.xend[IDIR] - d.xbeg[IDIR]);
    d.Ps(PX2,k) = d.xbeg[JDIR] + idfx::randm() * (d.xend[JDIR] - d.xbeg[JDIR]);
    d.Ps(PX3,k) = d.xbeg[KDIR] + idfx::randm() * (d.xend[KDIR] - d.xbeg[KDIR]);
    d.Ps(PVX1,k) = 2e-3 * (0.5 - idfx::randm());
    d.Ps(PVX2,k) = 2e-3 * (0.5 - idfx::randm());
    d.Ps(PVX3,k) = 2e-3 * (0.5 - idfx::randm());

    d.Ps(PMASS,k) = PM;
  }

  d.SyncToDevice();
}

// Analyse data to produce an output
void MakeAnalysis(DataBlock & data) {

}
