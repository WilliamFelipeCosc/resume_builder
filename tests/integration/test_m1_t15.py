import io
import subprocess

import pytest
from pypdf import PdfWriter
from resume_core.sources.pdf_metadata import PdfMetadataError, inspect_pdf


def pdf(pages=1, encrypted=False):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=100, height=100)
    if encrypted:
        writer.encrypt("synthetic-password")
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def test_m1_pdf_valid_metadata_only():
    assert inspect_pdf(pdf(pages=2)).page_count == 2


@pytest.mark.parametrize(
    ("data", "code"),
    [
        (b"invalid sentinel", "pdf_invalid"),
        (pdf(encrypted=True), "pdf_encrypted"),
        (pdf(pages=51), "pdf_pages_exceeded"),
        (b"x" * (10 * 1024 * 1024 + 1), "pdf_too_large"),
    ],
)
def test_m1_pdf_rejects_bad_input_without_echo(data, code):
    with pytest.raises(PdfMetadataError) as error:
        inspect_pdf(data)
    assert error.value.code == code
    assert "sentinel" not in str(error.value)


def test_m1_pdf_timeout_is_sanitized(monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("sensitive sentinel", 5)

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(PdfMetadataError) as error:
        inspect_pdf(pdf())
    assert error.value.code == "pdf_unavailable"
    assert "sentinel" not in str(error.value)


def test_m1_pdf_child_limits_and_environment(monkeypatch):
    import resume_core.sources.pdf_metadata as module

    def run(args, **kwargs):
        assert args[1] == "-I"
        assert kwargs["timeout"] == 5
        assert kwargs["stderr"] == subprocess.DEVNULL
        assert kwargs["env"] == {"PATH": module.os.defpath}
        return subprocess.CompletedProcess(args, 0, stdout=b"1")

    monkeypatch.setattr(subprocess, "run", run)
    assert inspect_pdf(b"synthetic").page_count == 1


def test_m1_pdf_worker_applies_memory_limit_without_text_extraction(monkeypatch, capsys):
    import logging
    import resource
    import sys
    from types import SimpleNamespace

    import pypdf
    import resume_core.sources.pdf_metadata as module

    limits = []
    monkeypatch.setattr(logging, "disable", lambda level: None)
    monkeypatch.setattr(resource, "setrlimit", lambda kind, value: limits.append((kind, value)))
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(b"synthetic")))

    class Reader:
        is_encrypted = False
        pages = [object()]

        def __init__(self, stream, strict):
            assert stream.read() == b"synthetic"
            assert strict is True

        def extract_text(self):
            raise AssertionError("text extraction is forbidden")

    monkeypatch.setattr(pypdf, "PdfReader", Reader)
    module._worker()
    assert limits == [(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))]
    assert capsys.readouterr().out == "1"


def test_m1_pdf_child_enforces_memory_and_discards_parser_warnings(tmp_path, monkeypatch, capfd):
    import resume_core.sources.pdf_metadata as module

    probe = tmp_path / "bounded_pdf_probe.py"
    probe.write_text(
        "import logging\n"
        "import mmap\n"
        "import sys\n"
        "import warnings\n"
        "import pypdf\n"
        "from resume_core.sources.pdf_metadata import _worker\n"
        "class Reader:\n"
        "    is_encrypted = False\n"
        "    pages = [object()]\n"
        "    def __init__(self, source, strict):\n"
        "        logging.warning('PDF_WARNING_SENTINEL')\n"
        "        warnings.warn('PDF_WARNING_SENTINEL')\n"
        "        sys.stderr.write('PDF_WARNING_SENTINEL')\n"
        "        if source.read() == b'large':\n"
        "            self.reservation = mmap.mmap(-1, 600 * 1024 * 1024)\n"
        "pypdf.PdfReader = Reader\n"
        "_worker()\n"
    )
    monkeypatch.setattr(module, "__file__", str(probe))
    assert module.inspect_pdf(b"control").page_count == 1
    with pytest.raises(PdfMetadataError) as error:
        module.inspect_pdf(b"large")
    assert error.value.code == "pdf_invalid"
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""
