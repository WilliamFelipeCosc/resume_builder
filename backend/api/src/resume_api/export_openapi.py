"""Export the public contract offline without creating data, sessions or broker connections."""

import argparse
import json
from pathlib import Path

from resume_api.app import create_app


def export(destination: Path) -> None:
    schema = create_app(service=None).openapi()
    destination.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    export(parser.parse_args().output)


if __name__ == "__main__":
    main()
