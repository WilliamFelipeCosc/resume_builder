"""Inspect PDF structure in a resource-limited subprocess."""

import os
import subprocess
import sys
from dataclasses import dataclass


class PdfMetadataError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class PdfMetadata:
    page_count: int


def inspect_pdf(data: bytes) -> PdfMetadata:
    if len(data) > 10 * 1024 * 1024:
        raise PdfMetadataError("pdf_too_large")
    try:
        result = subprocess.run(
            [sys.executable, "-I", __file__],
            input=data,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
            env={"PATH": os.defpath},
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PdfMetadataError("pdf_unavailable") from exc
    if result.returncode != 0:
        raise PdfMetadataError("pdf_invalid")
    output = result.stdout
    if output == b"encrypted":
        raise PdfMetadataError("pdf_encrypted")
    if output == b"pages_exceeded":
        raise PdfMetadataError("pdf_pages_exceeded")
    if not output.isdigit() or not 1 <= int(output) <= 50:
        raise PdfMetadataError("pdf_invalid")
    return PdfMetadata(page_count=int(output))


def _worker() -> None:
    import io
    import logging
    import resource

    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    logging.disable(logging.CRITICAL)
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(sys.stdin.buffer.read()), strict=True)
        if reader.is_encrypted:
            output = "encrypted"
        else:
            count = len(reader.pages)
            output = str(count) if count <= 50 else "pages_exceeded"
        sys.stdout.write(output)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    _worker()
