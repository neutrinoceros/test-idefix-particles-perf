set -euxo pipefail

idfx conf -gpu
idfx run --tstop 0.051
idfx digest --all -o report0.json
idfx run -restart
idfx clean --all --no-confirm
idfx digest --all -o report1.json
rm *.vtk *.dmp
