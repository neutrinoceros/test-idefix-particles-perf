set -euxo pipefail

idfx conf -mpi -gpu
idfx run --nproc 8 --tstop 0.52
idfx run --nproc 8 -restart
idfx clean --all --no-confirm
idfx digest --all -o report.json
