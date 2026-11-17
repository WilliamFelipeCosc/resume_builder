from uuid import uuid4

import pytest
from pydantic import ValidationError
from resume_core.career_kb.contracts import CONTENT_TYPES, CREATE_TYPES, READ_TYPES, PartialDate

SAMPLES = {
    "profile": {"fullName": "Synthetic Person"},
    "experience": {"companyNameOriginal": "Synthetic Co", "jobTitleOriginal": "Engineer"},
    "statement": {"textOriginal": "Synthetic statement"},
    "project": {"title": "Synthetic project"},
    "achievement": {"textOriginal": "Synthetic achievement", "metricValue": "about 10"},
    "skill": {"name": "Synthetic skill", "originalLabels": ["Alias"]},
    "education": {"institution": "Synthetic school", "programOriginal": "Course"},
    "language": {"language": "Synthetic language", "proficiencyOriginal": "basic"},
    "evidence": {
        "description": "Synthetic note",
        "evidenceKind": "manual_note",
        "sourceDocumentId": str(uuid4()),
    },
}


@pytest.mark.parametrize("kind", SAMPLES)
def test_m1_nine_content_types_round_trip(kind):
    model = CONTENT_TYPES[kind].model_validate(SAMPLES[kind])
    dumped = model.model_dump(mode="json", by_alias=True)
    assert CONTENT_TYPES[kind].model_validate(dumped) == model
    for key, value in SAMPLES[kind].items():
        assert dumped[key] == value


def test_m1_command_scope_and_field_classification():
    profile_id, source_id, key = str(uuid4()), str(uuid4()), str(uuid4())
    data = {
        "content": SAMPLES["skill"],
        "profileId": profile_id,
        "sourceDocumentId": source_id,
        "idempotencyKey": key,
        "fieldPrivacy": {"name": "secret"},
    }
    command = CREATE_TYPES["skill"].model_validate(data)
    assert command.privacy == "confidential" and command.field_privacy == {"name": "secret"}
    for change in (
        {"profileId": None},
        {"fieldPrivacy": {"unknown": "secret"}},
        {"fieldPrivacy": {"name": "public"}},
        {"principal": "attacker"},
    ):
        with pytest.raises(ValidationError):
            CREATE_TYPES["skill"].model_validate(data | change)
    profile = CREATE_TYPES["profile"].model_validate(
        data | {"content": SAMPLES["profile"], "profileId": None, "fieldPrivacy": {}}
    )
    assert profile.profile_id is None


def test_m1_read_distinguishes_unknown_and_restricted_profile_fields():
    payload = {
        "id": str(uuid4()),
        "revisionId": str(uuid4()),
        "privacy": "confidential",
        "content": {"fullName": None, "email": None},
        "restrictedFields": ["fullName"],
        "fieldConfirmations": {"email": "confirmed"},
    }
    result = READ_TYPES["profile"].model_validate(payload)
    assert result.content.full_name is None and result.content.email is None
    assert result.restricted_fields == ["fullName"]
    assert result.field_confirmations == {"email": "confirmed"}


def test_m1_read_rejects_restricted_values_and_invalid_field_types():
    payload = {
        "id": str(uuid4()),
        "revisionId": str(uuid4()),
        "privacy": "public",
        "content": {"name": "visible"},
        "restrictedFields": ["name"],
        "confirmation": "unverified",
    }
    with pytest.raises(ValidationError):
        READ_TYPES["skill"].model_validate(payload)
    for content in ({"name": "x" * 257}, {"explicitlyListedInSkillsSection": "true"}):
        with pytest.raises(ValidationError):
            READ_TYPES["skill"].model_validate(
                payload | {"content": content, "restrictedFields": []}
            )


@pytest.mark.parametrize(
    ("value", "precision"), [("2024", "year"), ("2024-02", "month"), ("2024-02-29", "day")]
)
def test_m1_partial_date_valid(value, precision):
    assert PartialDate(value=value, precision=precision).value == value


@pytest.mark.parametrize(
    ("value", "precision"),
    [("2023-02-29", "day"), ("2024-13", "month"), ("2024-01", "year"), ("0000", "year")],
)
def test_m1_partial_date_invalid(value, precision):
    with pytest.raises(ValidationError):
        PartialDate(value=value, precision=precision)


def test_m1_contract_rejects_coercion_extras_and_text_limits():
    for data in (
        {"name": 123},
        {"name": "ok", "extra": "x"},
        {"name": "ok", "explicitlyListedInSkillsSection": "true"},
        {"name": "x" * 257},
        {"name": "ok", "originalLabels": ["x" * 257]},
    ):
        with pytest.raises(ValidationError):
            CONTENT_TYPES["skill"].model_validate(data)
    with pytest.raises(ValidationError):
        CONTENT_TYPES["achievement"].model_validate({"textOriginal": "x" * 8001})
