import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import git
import os
import warnings

TESTS_DIR = Path(__file__).parent / "tests"
with open(TESTS_DIR / "names.json") as fh:
    test_cases = json.load(fh)


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
    file = Path(__file__).parent / "machine_label.txt"
    if file.is_file():
        try:
            return file.read_text().strip()
        except OSError:
            warnings.warn(f"failed to read {str(file)}")
            return ""
    else:
        warnings.warn(f"did not find {str(file)}")


fig, ax = plt.subplots(layout="constrained")
ax.set(
    xlabel="time",
    ylabel="perf (cell updates/s/proc)",
    yscale="log",
    title=(
        f"idefix version: {get_idefix_branch()} "
        f"({get_idefix_version_sha()})\n"
        f"running on {get_machine_label() or '???'}"
    ),
)
# fig.suptitle("Impact of particle fragmentation on performance")

for i_tc, tc in enumerate(test_cases):
    reports = sorted(TESTS_DIR.joinpath(tc).glob("*.json"))

    if not reports:
        continue

    print(f"plotting {tc}")
    color = f"C{i_tc}"
    nreports = len(reports)
    for i_report, (report, linestyle) in enumerate(zip(reports, ("-", "--")), start=1):
        series = pd.read_json(report, typ="series")
        stacked = np.empty((len(series.iloc[0]["time"]), len(series)), dtype="float")
        nprocs = len(series)

        for i, s in enumerate(series):
            stacked[:, i] = s["cell (updates/s)"]

        label = tc
        if nreports > 1:
            label += f" ({i_report}/{nreports})"

        ax.plot(
            series.iloc[0]["time"],
            stacked.mean(axis=1) / nprocs,
            color=color,
            linewidth=2,
            linestyle=linestyle,
            label=label,
        )

        if tc == "no_particles":
            # Illustrate the ideal 'goal' perf (that is advertised in our proposal)
            target_value = np.nanmean(stacked) / (1 + 8)
            ann_kwargs = {"color": "black", "alpha": 0.6}
            ax.axhline(target_value, ls=":", **ann_kwargs)
            ax.annotate("target performance", (0.05, target_value * 1.1), **ann_kwargs)

fig.legend(ncol=2, loc="outside lower center")

if label := get_machine_label():
    machine_suffix = f"_{label}"
else:
    machine_suffix = ""
sfile = f"perfs{machine_suffix}_{get_idefix_version_sha()}.png"
print(f"saving to {sfile}")
fig.savefig(sfile)
