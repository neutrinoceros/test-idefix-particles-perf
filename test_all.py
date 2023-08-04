import subprocess
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    from contextlib import chdir
else:
    from idefix_cli.lib import chdir

HERE = Path(__file__).parent

tests_cases = [
    "baseline",
    "max_frag",
    "min_frag",
    "no_particles",
    "with_restart",
]

for tc in tests_cases:
    print(f"Running {tc} ...")
    with chdir((HERE / tc).resolve()):
        subprocess.run(["bash", "test.sh"], check=True)
