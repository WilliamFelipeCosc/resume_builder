import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path("tools/check_milestone_drift.py")


def test_record_has_required_milestones_and_exception_evidence() -> None:
    record = json.loads(Path("docs/process/milestone-status.json").read_text())
    milestones = record["milestones"]
    assert set(milestones) == {"M0", "M0.5", "M1", "M2", "M3", "M4", "M5", "M6", "M7"}
    allowed = {
        "planned",
        "in_progress",
        "implemented",
        "verified",
        "accepted",
        "accepted_with_exception",
    }
    assert all(entry["status"] in allowed for entry in milestones.values())
    if milestones["M0.5"]["status"] == "accepted_with_exception":
        assert any("SPIKE-17" in item for item in milestones["M0.5"]["exceptions"])
    assert all(
        entry["criteria"] and Path(entry["evidence"]).is_file() for entry in milestones.values()
    )


def run_check(snapshot: Path, record: Path | None = None) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), str(snapshot)]
    if record is not None:
        command.extend(["--record", str(record)])
    return subprocess.run(command, capture_output=True, text=True)


def test_matching_snapshot_is_read_only(tmp_path: Path) -> None:
    record = json.loads(Path("docs/process/milestone-status.json").read_text())
    snapshot = tmp_path / "vault.json"
    statuses = {k: v["status"] for k, v in record["milestones"].items()}
    snapshot.write_text(json.dumps({"milestones": statuses, "index": statuses}))
    before = snapshot.read_bytes()
    result = run_check(snapshot)
    assert result.returncode == 0
    assert "No milestone status drift" in result.stdout
    assert snapshot.read_bytes() == before


def test_changed_and_missing_statuses_are_reported(tmp_path: Path) -> None:
    record = tmp_path / "record.json"
    record.write_text(
        '{"milestones": {"M0": {"status": "accepted"}, '
        '"M0.5": {"status": "accepted_with_exception"}}}'
    )
    snapshot = tmp_path / "vault.json"
    snapshot.write_text('{"milestones": {"M0": "planned"}, "index": {}}')
    result = run_check(snapshot, record)
    assert result.returncode == 1
    assert "M0: repository=accepted, Obsidian=planned" in result.stdout
    assert "M0.5: repository=accepted_with_exception, Obsidian=<missing>" in result.stdout


def test_unavailable_or_invalid_snapshot_is_not_a_pass(tmp_path: Path) -> None:
    snapshot = tmp_path / "vault.json"
    assert run_check(snapshot).returncode == 2
    snapshot.write_text("not json")
    result = run_check(snapshot)
    assert result.returncode == 2
    assert "Synchronization not checked" in result.stderr
