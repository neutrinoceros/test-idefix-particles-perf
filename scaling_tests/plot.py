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
    for datafile in natsorted(args.directory.glob("*.json")):
        if (
            m := re.fullmatch(r"s(?P<size>\d+)_n(?P<nproc>\d+).json", datafile.name)
        ) is not None:
            sizes.append(int(m.group("size")))
            nprocs.append(int(m.group("nproc")))
        series = pd.read_json(datafile, typ="series")
        data = np.array(series[0]["cell (updates/s)"][1:])
        mean_perfs.append(np.mean(data))

    fig, ax = plt.subplots()
    ax.set(
        xlabel="number of processes",
        ylabel="Perfs [cell update/s]",
        yscale="log",
        title=(
            f"idefix version: {get_idefix_branch()} "
            f"({get_idefix_version_sha()})\n"
            f"running on {get_machine_label() or '???'}"
        ),
    )
    ax.scatter(nprocs, mean_perfs, c=sizes)

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
