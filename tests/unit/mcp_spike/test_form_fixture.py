"""The fake application form contains no answers or submission behavior."""

import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "data/synthetic/mcp-spike"


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.fields = {}
        self.labels = set()
        self.tags = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag in {"input", "textarea"}:
            self.fields[attrs.get("id")] = attrs
        if tag == "label":
            self.labels.add(attrs.get("for"))

    def handle_data(self, data):
        self.text.append(data)


def parse():
    result = FormParser()
    result.feed((ROOT / "form.html").read_text())
    return result


def test_four_fields_are_explicitly_labelled():
    form = parse()
    expected = {"fullName", "email", "targetRole", "approvedAnswer"}
    assert set(form.fields) == expected
    assert form.labels == expected


def test_form_has_no_fixture_values():
    html = (ROOT / "form.html").read_text()
    fixture = json.loads((ROOT / "context.json").read_text())
    for value in fixture["formValues"].values():
        assert value not in html
    for attrs in parse().fields.values():
        assert "value" not in attrs


def test_no_script_or_submitting_control():
    tags = parse().tags
    assert all(tag != "script" and "onsubmit" not in attrs for tag, attrs in tags)
    assert all(attrs.get("type") != "submit" for _, attrs in tags)
    assert all("action" not in attrs for tag, attrs in tags if tag == "form")


def test_page_identifies_fictional_experiment():
    text = " ".join(parse().text).lower()
    assert "fictíc" in text
    assert "demonstração" in text
