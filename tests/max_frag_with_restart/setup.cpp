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

  real margin[DIMENSIONS];
  real width[DIMENSIONS];
  for(int dir=0; dir<DIMENSIONS; dir++) {
    width[dir] = d.xend[dir] - d.xbeg[dir];
    margin[dir] = width[dir] * 0.05;
  }

  // put particles in sub-domain corners (with a small margin to avoid exact overlaps)
  for(int k = 0; k < d.nParticles; k++) {
    d.Ps(PX1,k) = d.xbeg[IDIR];
    d.Ps(PX1,k) += (k % 2) < 1 ? margin[IDIR] : width[IDIR] - margin[IDIR];
    d.Ps(PX2,k) = d.xbeg[JDIR];
    d.Ps(PX2,k) += (k % 4) < 2 ? margin[JDIR] : width[JDIR] - margin[JDIR];
    d.Ps(PX3,k) = d.xbeg[KDIR];
    d.Ps(PX3,k) += (k % 8) < 4 ? margin[KDIR] : width[KDIR] - margin[KDIR];
    d.Ps(PVX1,k) = ZERO_F;
    d.Ps(PVX2,k) = ZERO_F;
    d.Ps(PVX3,k) = ZERO_F;

    d.Ps(PMASS,k) = PM;

    // add particle velocity in a process-dependent direction
    //d.Ps(DIMENSIONS + idfx::prank%DIMENSIONS, k) = pow(-1, k) * ONE_F;

    // kill one-out-of two particles
    if(k%2==0) d.PisActive(k) = false;
  }
  d.SyncToDevice();
}

// Analyse data to produce an output
void MakeAnalysis(DataBlock & data) {

}
