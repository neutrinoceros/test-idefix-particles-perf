import argparse
import os
import sys
from pathlib import Path
from subprocess import run, CalledProcessError

import inifix


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
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

    options = inifix.load(args.directory / "config.ini")
    for sdir in os.listdir(args.directory):
        if not (args.directory / sdir).is_dir():
            continue
        print(f"visiting {args.directory/sdir}", file=sys.stderr)
        cmd = [
            "idfx",
            "digest",
            "--dir",
            str(args.directory / sdir),
        ]
        if "digest_input" in options:
            cmd.extend(["--input", options["digest_input"]])
        try:
            ret = run(cmd, capture_output=True, check=True)
        except CalledProcessError as exc:
            print(exc.stderr.decode(), file=sys.stderr)
            return 1

        out_file = args.directory.joinpath(sdir).with_suffix(".json")
        out_file.write_text(ret.stdout.decode())

    return 0


if __name__ == "__main__":
    sys.exit(main())
