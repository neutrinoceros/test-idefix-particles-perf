import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

tests_cases = [
    "baseline",
    "max_frag",
    "min_frag",
    "no_particles",
    "with_restart",
]

fig, ax = plt.subplots()
ax.set(
    xlabel="time",
    ylabel="perf (cell updates/s)",
    yscale="log",
)

for i_tc, tc in enumerate(tests_cases):
    report = os.path.join(tc, "report.json")
    if not os.path.isfile(report):
        continue

    print(f"plotting {tc}")

    series = pd.read_json(report, typ="series")
    stacked = np.empty((len(series[0]["time"]), len(series)), dtype="float")
    color = f"C{i_tc}"
    for i, s in enumerate(series):
        stacked[:, i] = s["cell (updates/s)"]
    #    ax.plot("time", "cell (updates/s)", data=s, lw=0.3, alpha=0.7, color=color)

    ax.plot(
        series[0]["time"],
        stacked.mean(axis=1),
        color=color,
        lw=2,
        label=tc,
    )

ax.legend()
sfile = "perfs.png"
print(f"saving to {sfile}")
fig.savefig(sfile)
