import argparse
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from natsort import natsorted
import git
import os
import warnings
from collections import defaultdict
from more_itertools import unzip


def get_idefix_version_sha() -> str:
    """return abreviated sha"""
    repo = git.Repo(os.environ["IDEFIX_DIR"])
    return repo.head.object.hexsha[:7]


def get_idefix_branch():
    repo = git.Repo(os.environ["IDEFIX_DIR"])
    try:
        return repo.active_branch
    except TypeError:
        # this may happen when idefix is in detached-HEAD view
        return ""


def get_machine_label():
    file = Path(__file__).parents[1] / "machine_label.txt"
    if file.is_file():
        try:
            return file.read_text().strip()
        except OSError:
            warnings.warn(f"failed to read {str(file)}")
            return ""
    else:
        warnings.warn(f"did not find {str(file)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", dest="directory", required=True, type=Path)
    args = parser.parse_args(argv)

    sizes: list[int] = []
    nprocs: list[int] = []
    mean_perfs = []
    datafiles = natsorted(args.directory.glob("*.json"))
    for datafile in datafiles:
        if (
            m := re.fullmatch(r"s(?P<size>\d+)_n(?P<nproc>\d+).json", datafile.name)
        ) is not None:
            sizes.append(int(m.group("size")))
            nprocs.append(int(m.group("nproc")))
        series = pd.read_json(datafile, typ="series")
        data = np.array(series[0]["cell (updates/s)"][1:])
        mean_perfs.append(np.mean(data))

    parallel_efficiency = np.empty_like(mean_perfs)
    for i, perf in enumerate(mean_perfs):
        size0 = sizes[i]
        nproc0 = nprocs[i]
        for j, (size, nproc) in enumerate(zip(sizes, nprocs)):
            if size == size0 and nproc == 1:
                i0 = j
                break
        else:
            raise RuntimeError("Failed to locate reference point")

        parallel_efficiency[i] = perf / nproc0 / mean_perfs[i0]

    # group data_files by problem size
    groups: dict[int, list[tuple(int, float)]] = defaultdict(list)
    for datafile, nproc, mean_perf, eff, size in zip(
        datafiles, nprocs, mean_perfs, parallel_efficiency, sizes
    ):
        groups[size].append((nproc, mean_perf, eff))
    curves = {
        k: {
            "nproc": np.array(list(unzip(v)[0])),
            "perf": np.array(list(unzip(v)[1])),
            "eff": np.array(list(unzip(v)[2])),
        }
        for k, v in groups.items()
    }

    fig, axs = plt.subplots(
        nrows=2, layout="constrained", sharex=True, gridspec_kw=dict(hspace=0, wspace=0)
    )
    for ax in axs.flat:
        ax.label_outer(remove_inner_ticks=True)
    ax = axs[0]
    ax.set(
        ylabel="Perfs [cell update/s]",
        xscale="log",
        yscale="log",
        title=(
            f"idefix version: {get_idefix_branch()} "
            f"({get_idefix_version_sha()})\n"
            f"running on {get_machine_label() or '???'}"
        ),
    )

    for size, curve in curves.items():
        ax.plot("nproc", "perf", marker="x", label=f"${size}^3$", data=curve)
    ax.legend()

    ax = axs[1]
    ax.set(
        xlabel="number of processes",
        ylabel="Parallel efficiency",
    )

    for curve in curves.values():
        ax.plot("nproc", "eff", marker="x", data=curve)

    # ax.scatter(nprocs, parallel_efficiency, c=sizes)

    if label := get_machine_label():
        machine_suffix = f"_{label}"
    else:
        machine_suffix = ""
    sfile = f"weakscaling{machine_suffix}_{get_idefix_version_sha()}.png"
    print(f"saving to {sfile}")
    fig.savefig(sfile)

    return 0


if __name__ == "__main__":
    sys.exit(main())
