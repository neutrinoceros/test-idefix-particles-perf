# Fragmentation tests

## Historical description (rationale)

*Fragmentation* and *entropy* are two loosely defined metric I use to quantify the state of memory where particle data is stored.
Both should ideally be 0 in initial conditions. Fragmentation is by construction 0 in initial conditions *and* at restart.

Both effects may be responsible for very noticeable performance degradation. The goal is to quantify these penalties (separately).

> Fragmentation
> I'm calling "fragmentation" a metric that evaluates to 0 if active and inactive particles both occupy contiguous memory spaces, and `>0` otherwise. It's not clear yet how to quantify the `>0` (general) case, but it may not be necessary if we discover that the performance penalty of *slight* fragmentation is roughly the same as maximal fragmentation.

>Entropy
>I'm calling "entropy" a metric that evaluates to 0 if active particles are maximally sorted in memory according to their position in space (the exact sorting algorithm isn't specified, but dimensions should be ordered the same as they are on grid-defined arrays.

Note that, both effects are expected to worsen as the simulation progresses (but fragmentation may be kept at bay with smart enough memory management in MPI exchange routine). The "obvious" solution to growing entropy is to periodically sort particles. We could also elect a sorting algorithm suited to reduce/cancel fragmentation, but it might make things more complicated than necessary; Indeed, we expect fragmentation to degrade performance for 2 distinct reasons:
- increasing the physical distance (in memory) between the first and the last active particles implies longer loops (CPU)
- "holes" (inactive particles within the active range) destroy branch predictability (CPU) and hinder GPU vectorization (making some workers wait instead of participate to computation). I expect this latter effect to be much wors

All proposed tests are aimed to measure raw performance (cell updates/s) VS simulation time in various conditions.
In all cases, fluid/particle interaction should be suppressed and particle velocity should be 0 (so no particle is ever exchanged and we keep constant fragmentation/entropy throughout a run).

Tests:
- (`no_particles`) ZERO particles (don't even activate the module)
- (`baseline`) ICs with 0 entropy
- (`max_frag`) ICs with 0 entropy and maximal fragmentation
- (`max_frag_with_restart`) restart baseline after performance has degraded to a more or less constant value (based-off max_frag)
- (`randomized`) ICs with maximal entropy (randomized positions) and 0 fragmentation
- (`randomized_max_frag`) ICs with maximal entropy *and* maximal fragmentation
- (`max_frag_with_restart_mpi`) identical to max_frag_with_restart but runs twice as big a
  problem on 2 processes.


## Analysis

> Python>=3.9 is required. Python>=3.12 may work but hasn't been tested.

Install requirements as
```shell
$ python -m pip install ../requirements.txt
```

Run all tests as
```shell
python run_all.py
```

Finally, produce the result plot with
```shell
python plot.py
```

> The plotting scripts looks for a file named `machine_label.txt` at the root of the
> repository. If it exists, its content will be included in the figure's title as well
> as the resulting file's name. This allows to later gather results from more than one
> machine to a unified location without name collisions.

## End result

These tests demonstrated that entropy, and to a lesser extent fragmentation, came with
significant performance penalties. This justified the implementation of a sorting
algorithm in Idefix (triggered periodically).
