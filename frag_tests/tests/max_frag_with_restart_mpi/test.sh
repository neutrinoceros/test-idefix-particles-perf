set -euxo pipefail

idfx conf -gpu -mpi
idfx run --nproc 2 --tstop 0.051
idfx digest --all -o report0.json
idfx run --nproc 2 -restart
idfx clean --all --no-confirm
idfx digest --all -o report1.json
rm *.vtk *.dmp *.log
