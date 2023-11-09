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


def plot_perf(
    *,
    axs,
    datafiles: list[str],
    sn_regexp: str,
    legends: bool,
    **kwargs,
) -> None:
    MARKERS = ["h", "d", "X", "^", "x"]
    sizes: list[int] = []
    nprocs: list[int] = []
    mean_perfs = []

    for datafile in datafiles:
        if (m := re.fullmatch(sn_regexp, datafile.name)) is not None:
            sizes.append(int(m.group("size")))
            nprocs.append(int(m.group("nproc")))
        series = pd.read_json(datafile, typ="series")
        data = np.array(series.iloc[0]["cell (updates/s)"][1:])
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
    for k in curves.keys():
        curves[k]["perf/proc"] = curves[k]["perf"] / curves[k]["nproc"]

    for i, (curve, marker) in enumerate(zip(curves.values(), MARKERS)):
        axs[0].plot(
            "nproc", "perf/proc", color=f"C{i}", marker=marker, data=curve, **kwargs
        )

    artists = []
    for i, ((size, curve), marker) in enumerate(zip(curves.items(), MARKERS)):
        (handle,) = axs[1].plot(
            "nproc",
            "eff",
            color=f"C{i}",
            marker=marker,
            data=curve,
            label=f"${size}^3$",
            **kwargs,
        )
        artists.append(handle)
    return artists


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", dest="directory", required=True, type=Path)
    args = parser.parse_args(argv)

    # init figure
    fig, axs = plt.subplots(
        nrows=2, layout="constrained", sharex=True, gridspec_kw=dict(hspace=0, wspace=0)
    )
    for ax in axs.flat:
        ax.label_outer(remove_inner_ticks=True)
    ax = axs[0]
    ax.set(
        ylabel="Perfs [cell update/s/process]",
        xscale="log",
        yscale="log",
        title=(
            f"idefix version: {get_idefix_branch()} "
            f"({get_idefix_version_sha()})\n"
            f"running on {get_machine_label() or '???'}"
        ),
    )
    sax = ax.secondary_yaxis("right", functions=(lambda x: x * 8, lambda x: x / 8))
    sax.set(ylabel="Perfs [particle update/s/process]")

    axs[1].set(
        xlabel="number of processes",
        ylabel="Parallel efficiency",
    )

    particle_datafiles = natsorted(args.directory.glob("s*.json"))
    wp_artists = plot_perf(
        axs=axs,
        datafiles=particle_datafiles,
        sn_regexp=r"s(?P<size>\d+)_n(?P<nproc>\d+).json",
        legends=True,
    )

    particlefree_datafiles = natsorted(args.directory.glob("NPs*.json"))
    plot_perf(
        axs=axs,
        datafiles=particlefree_datafiles,
        sn_regexp=r"NPs(?P<size>\d+)_n(?P<nproc>\d+).json",
        legends=False,
        linestyle="--",
        alpha=0.6,
    )

    # finalize figure
    axs[1].legend(handles=wp_artists, frameon=False)

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
