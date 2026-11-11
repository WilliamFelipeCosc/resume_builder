"""Check committed schema and SDK twice in temporary directories; never rewrite real artifacts."""

import subprocess
import tempfile
from pathlib import Path

from resume_api.export_openapi import export


def contents(directory):
    return {
        path.relative_to(directory): path.read_bytes()
        for path in directory.rglob("*")
        if path.is_file()
    }


def main():
    root = Path(__file__).resolve().parents[1]
    package = root / "packages/api-client"
    expected = contents(package / "src/generated")
    with tempfile.TemporaryDirectory(prefix="rb-contract-", dir="/tmp") as directory:
        temporary = Path(directory)
        schema = temporary / "openapi.json"
        export(schema)
        if schema.read_bytes() != (package / "openapi.json").read_bytes():
            raise SystemExit("OpenAPI differs: run just generate and review the contract.")
        for index in range(2):
            output = temporary / f"sdk-{index}"
            subprocess.run(
                [
                    "pnpm",
                    "--filter",
                    "@resume-builder/api-client",
                    "exec",
                    "openapi-ts",
                    "-i",
                    str(schema),
                    "-o",
                    str(output),
                ],
                cwd=root,
                check=True,
            )
            if contents(output) != expected:
                raise SystemExit(
                    "Generated SDK differs: run just generate and review the contract."
                )
    print("OpenAPI and generated SDK: PASS (two identical generations)")


if __name__ == "__main__":
    main()
