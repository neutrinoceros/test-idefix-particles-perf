import subprocess
import sys
from pathlib import Path
import json

if sys.version_info >= (3, 11):
    from contextlib import chdir
else:
    from idefix_cli.lib import chdir

TESTS_DIR = Path(__file__).parent / "tests"
with open(TESTS_DIR / "names.json") as fh:
    test_cases = json.load(fh)


for tc in test_cases:
    print(f"Running {tc} ...")
    with chdir(TESTS_DIR / tc):
        subprocess.run(["bash", "test.sh"], check=True)
