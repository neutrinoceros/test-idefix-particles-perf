set -euxo pipefail

idfx conf -mpi -gpu
idfx run --nproc 8
idfx digest --all -o report.json

