set -euxo pipefail

idfx conf -mpi -gpu
idfx run --nproc 8 --tstop 0.52
idfx digest --all -o report0.json
idfx run --nproc 8 -restart
idfx clean --all --no-confirm
idfx digest --all -o report1.json
rm *.vtk *.dmp
