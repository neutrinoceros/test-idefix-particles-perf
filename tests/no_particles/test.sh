set -euxo pipefail

idfx conf -gpu
idfx run
idfx clean --all --no-confirm
idfx digest --all -o report.json
rm *.vtk *.dmp
