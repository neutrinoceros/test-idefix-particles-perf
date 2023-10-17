import argparse
import itertools as itt
import sys
from pathlib import Path
from subprocess import run
from typing import Any

import inifix
import numpy as np
from inifix.format import iniformat

if sys.version_info >= (3, 11):
    from contextlib import chdir
else:
    from idefix_cli.lib import chdir


BASE_SETUP_PATH = Path(__file__).parent.joinpath("base_setup").resolve()

SAMPLE_CONF = iniformat("size_range 8 32\n" "nproc_range 1 4\n" "conf_flags -mpi -gpu")


def is_power_of_two(n) -> bool:
    return (n != 0) and (n & (n - 1) == 0)


def range_power_of_two(vmin, vmax, /) -> "np.array[Any, np.dtype[np.int32]]":
    return 2 ** np.arange(np.log2(vmin), np.log2(2 * vmax), dtype="int32")


def submit(*, problem_size: int, nproc: int, output_dir: Path) -> None:
    """
    Run ONE simulation. This is meant to be looped at the above level.
    """
    if not is_power_of_two(nproc):
        raise ValueError(f"Expected nproc to be a power of two, got {nproc}")
    if not is_power_of_two(problem_size):
        raise ValueError(
            f"Expected problem_size to be a power of two, got {problem_size}"
        )

    # map (nproc, size) -> (domain_dec, grid_shape)
    domain_dec = np.ones(3, dtype="int32")
    grid_shape = np.full(3, problem_size, dtype="int32")
    domain_scale = np.ones(3, dtype="int32")

    div, mod = divmod(nproc, 8)
    while mod == 0:
        domain_dec[:] *= 2
        domain_scale[:] *= 2
        div, mod = divmod(nproc, 8)

    if nproc >= 2:
        if (nproc % 4) == 0:
            domain_dec[:2] *= 2
            domain_scale[:2] *= 2
        elif (nproc % 2) == 0:
            domain_dec[0] *= 2
            domain_scale[0] *= 2

    assert np.prod(domain_dec) == nproc
    grid_shape *= domain_scale

    setup_path = output_dir / f"s{problem_size}_n{nproc}"
    run(
        [
            "idfx",
            "clone",
            str(BASE_SETUP_PATH),
            str(setup_path),
            "--include",
            "idefix",
        ],
        check=True,
    )

    inifile = setup_path / "idefix.ini"
    conf = inifix.load(inifile)
    for idir in range(3):
        conf["Grid"][f"X{idir+1}-grid"] = [
            1,
            0.0,
            int(grid_shape[idir]),
            "u",
            float(domain_scale[idir]),
        ]
    inifix.dump(conf, inifile)
    with chdir(setup_path):
        cmd = [
            "mpirun",
            "-n",
            str(nproc),
            "./idefix",
            "-nowrite",
            "-dec",
            *(str(_) for _ in domain_dec),
        ]
        # TODO: replace subprocess.run with an actual job submission
        run(cmd, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_file",
        type=Path,
        help="Input file",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=Path,
        help="Output directory",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite any existing results (no clean up is performed)",
    )
    args = parser.parse_args(argv)
    if args.input_file is None:
        print(
            f"Please specify an --input_file "
            f"Here's a sample configuration\n\n{SAMPLE_CONF}",
            file=sys.stderr,
        )
        return 1
    if not args.input_file.is_file():
        print(
            f"No such file {args.input_file} ",
            file=sys.stderr,
        )
        return 1
    if args.output_dir is None:
        print(
            "Please specify an --output_dir ",
            file=sys.stderr,
        )
        return 1
    if args.output_dir.exists() and not args.force:
        print(
            f"Error: {args.output_dir} already exists. "
            "Pass the --force flag to ignore this error, "
            "or use another directory name.",
            file=sys.stderr,
        )
        return 1
    args.output_dir.mkdir(exist_ok=True)

    options = inifix.load(args.input_file, parse_scalars_as_lists=True)

    if not all(
        is_power_of_two(_) for _ in (*options["size_range"], *options["nproc_range"])
    ):
        print("Error in configuration: expected all values to be powers of two")
        return 1

    sizes = range_power_of_two(*options["size_range"])
    nprocs = range_power_of_two(*options["nproc_range"])

    with chdir(BASE_SETUP_PATH):
        run(["idfx", "clean", "--all", "--no-confirm"], check=True)
        run(["idfx", "conf", *options["conf_flags"]], check=True)
        run(["make", "-j8"], check=True)

    for size, nproc in itt.product(sizes, nprocs):
        submit(problem_size=size, nproc=nproc, output_dir=args.output_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
