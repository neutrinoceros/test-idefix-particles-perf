# Scaling tests

This directory contains weak scaling tests for the particle module.

The base setup is a 3D, cartesian, periodic and cubic box. The size of the box  attached to a process (in each
direction) can be varied, as well as the number of processes, in powers of two only.
The total size of the problem scales with the number of processes, extending the global box in factors of 2 in the x, y, and z direction (in this order) and cycling back.
Each simulation is run in 2 flavours: with 8 particles per cell and without particles at all (in which case the module isn't activated).

## Requirements
Install requirements as
```shell
$ python -m pip install ../requirements.txt
```

## Usage
The pipeline is comprised of 3 Python scripts:
1 `run.py`
1 `reduce.py`
1 `plot.py`

### Run simulations

The first step is to create a configuration file to parametrize the test matrix.

Here's an example of such a file
```ini
# config.ini
size_range     16    128
nproc_range    1     256
conf_flags     -mpi  -gpu -arch Volta70
make_flags     -j4
job_template   jean-zay_v100.slurm
```
`size_range` and `nproc_range` parametrize the minimum and maximum box size (process level) and number of processes respectively, and are mandatory.
All other fields are optional.

Simulations are run (or submitted through a job scheduler) as
```shell
python run.py -i config.ini -o $OUTPUT
```

where `$OUTPUT` represents the output directory

### Reduce results
```shell
python reduce.py --dir $OUTPUT
```

### Generate plot
```shell
python plot.py --dir $OUTPUT
```

Note that, by default, the resulting plot will contain information about the currently checked-out
branch/commit sha in $IDEFIX_DIR. This is determined at runtime, so it may not reflect the branch that was actually used to run simulations.
The name of the machine is also included by default. The script looks for a file named `machine_label.txt` at the top level of this repository.

It is possible to override this default behaviour by supplying a custom figure title on the command line (e.g. `--title 'example title'`). You can also suppress the title altogether by passing `--title ''`.
