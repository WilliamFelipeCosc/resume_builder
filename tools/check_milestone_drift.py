"""Compare a read-only Obsidian status snapshot with the repository record."""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="JSON snapshot exported from Obsidian")
    parser.add_argument("--record", type=Path, default=Path("docs/process/milestone-status.json"))
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        expected = record["milestones"]
        actual = snapshot["milestones"]
        index = snapshot["index"]
        if (
            not isinstance(expected, dict)
            or not expected
            or not isinstance(actual, dict)
            or not isinstance(index, dict)
        ):
            raise ValueError("milestones must be JSON objects")
        if not all(
            isinstance(v, dict) and isinstance(v.get("status"), str) for v in expected.values()
        ):
            raise ValueError("record entries must include status strings")
        if not all(isinstance(v, str) for values in (actual, index) for v in values.values()):
            raise ValueError("snapshot milestone values must be status strings")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Synchronization not checked: {exc}", file=sys.stderr)
        return 2

    drift = False
    for view, values in (("notes", actual), ("index", index)):
        for milestone, entry in expected.items():
            observed = values.get(milestone)
            if observed != entry["status"]:
                print(
                    f"{view} {milestone}: repository={entry['status']}, Obsidian={observed or '<missing>'}"
                )
                drift = True
        for milestone in values.keys() - expected.keys():
            print(f"{view} {milestone}: repository=<missing>, Obsidian={values[milestone]}")
            drift = True
    if drift:
        return 1
    print("No milestone status drift in supplied snapshot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
