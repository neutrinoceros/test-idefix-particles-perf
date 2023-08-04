#include "idefix.hpp"
#include "setup.hpp"

real PM; // particle mass

// Initialisation routine. Can be used to allocate
// Arrays or variables which are used later on
Setup::Setup(Input &input, Grid &grid, DataBlock &data, Output &output) {
  PM = input.Get<real>("Setup", "mass", 0);
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

  d.SyncToDevice();
}

// Analyse data to produce an output
void MakeAnalysis(DataBlock & data) {

}
