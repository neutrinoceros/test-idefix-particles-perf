import subprocess
from contextlib import chdir
from pathlib import Path

HERE = Path(__file__).parent

tests_cases = [
    "baseline",
    "max_frag",
    "min_frag",
    "no_particles",
    "with_restart",
]

for tc in tests_cases:
    with chdir((HERE/tc).resolve()):
        subprocess.run(["bash", "test.sh"], check=True)
