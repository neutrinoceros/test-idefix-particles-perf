import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import git
import os

TESTS_DIR = Path(__file__).parent / "tests"
with open(TESTS_DIR / "names.json") as fh:
    test_cases = json.load(fh)


def get_idefix_version_sha():
    repo = git.Repo(os.environ["IDEFIX_DIR"])
    return repo.head.object.hexsha


def get_idefix_branch():
    repo = git.Repo(os.environ["IDEFIX_DIR"])
    return repo.active_branch


fig, ax = plt.subplots(layout="constrained")
ax.set(
    xlabel="time",
    ylabel="perf (cell updates/s)",
    yscale="log",
    title=f"idefix version: {get_idefix_branch()}\n{get_idefix_version_sha()}",
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
        stacked = np.empty((len(series[0]["time"]), len(series)), dtype="float")

        for i, s in enumerate(series):
            stacked[:, i] = s["cell (updates/s)"]

        label = tc
        if nreports > 1:
            label += f" ({i_report}/{nreports})"

        ax.plot(
            series[0]["time"],
            stacked.mean(axis=1),
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
sfile = f"perfs_{get_idefix_version_sha()}.png"
print(f"saving to {sfile}")
fig.savefig(sfile)
