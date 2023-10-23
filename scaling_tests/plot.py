import argparse
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from natsort import natsorted


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
            sizes.append(m.group("size"))
            nprocs.append(m.group("nproc"))
        series = pd.read_json(datafile, typ="series")
        data = np.array(series[0]["cell (updates/s)"][1:])
        mean_perfs.append(np.mean(data))

    fig, ax = plt.subplots()
    ax.set(
        xlabel="number of processes",
        ylabel="Perfs [cell update/s]",
        yscale="log",
    )
    ax.scatter(nprocs, mean_perfs)

    sfile = "/tmp/test.png"
    print(f"saving to {sfile}")
    fig.savefig(sfile)


if __name__ == "__main__":
    sys.exit(main())
