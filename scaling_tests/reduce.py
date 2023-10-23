import argparse
import os
import sys
from pathlib import Path
from subprocess import run

import inifix


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="input", required=True, type=Path, help="configuration"
    )
    parser.add_argument(
        "--dir",
        dest="directory",
        required=True,
        type=Path,
        help="directory containing tests",
    )

    args = parser.parse_args(argv)

    if not args.directory.is_dir():
        print(f"no such directory {args.directory}", file=sys.stderr)
        return 1

    options = inifix.load(args.input)

    os.makedirs("results", exist_ok=True)
    for sdir in os.listdir(args.directory):
        cmd = [
            "idfx",
            "digest",
            "--dir",
            os.path.join(args.directory, sdir),
        ]
        if "digest_input" in options:
            cmd.extend(["--input", options["digest_input"]])
        ret = run(cmd, capture_output=True, check=True)

        with open(os.path.join("results", sdir) + ".json", "wt") as fh:
            fh.write(ret.stdout.decode())

    return 0


if __name__ == "__main__":
    sys.exit(main())
