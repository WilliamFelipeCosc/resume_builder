import json
from pathlib import Path

from resume_core.mcp_spike.contracts import ApplicationContext, check_json_size

FIXTURE = Path(__file__).resolve().parents[3] / "data/synthetic/mcp-spike/context.json"


def test_context_fixture_conforms_to_contract():
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    context = ApplicationContext.model_validate(raw)
    assert context.model_dump(by_alias=True) == raw
    assert check_json_size(raw, 16384) <= 16384


def test_context_is_the_approved_synthetic_application():
    context = ApplicationContext.model_validate_json(FIXTURE.read_text(encoding="utf-8"))
    assert context.application_id == "app-demo"
    assert context.form_values.approved_answer in context.approved_answers


def test_references_are_synthetic_identifiers():
    context = ApplicationContext.model_validate_json(FIXTURE.read_text(encoding="utf-8"))
    assert context.evidence_refs
    assert all(ref.startswith("synthetic-") for ref in context.evidence_refs)


def test_fixture_states_synthetic_and_no_submission_restrictions():
    context = ApplicationContext.model_validate_json(FIXTURE.read_text(encoding="utf-8"))
    assert "Dados fictícios para demonstração." in context.restrictions
    assert "Não enviar candidatura." in context.restrictions
