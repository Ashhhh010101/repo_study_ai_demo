import pytest
from pydantic import ValidationError

from app.repo_analyzer.report_builder import (
    build_basic_markdown_report,
    derive_report_fields,
)
from app.schemas.analysis import FileSummary
from app.services.report_service import ReportService


def test_file_summary_schema_rejects_missing_required_fields():
    with pytest.raises(ValidationError):
        FileSummary.model_validate({"purpose": "Only a purpose is present."})


def test_report_fields_extract_markdown_sections():
    markdown = """# Demo

## 1. Project Overview
Concrete overview from `src/main.py`.

## 4. Runtime Architecture and Component Responsibilities
The API starts in `src/main.py`.
"""
    fields = derive_report_fields(markdown, {}, {}, [])

    assert fields["overview"] == "Concrete overview from `src/main.py`."
    assert fields["architecture_summary"] == "The API starts in `src/main.py`."


def test_local_fallback_has_complete_report_contract():
    markdown = build_basic_markdown_report("demo", {}, [], {})

    assert ReportService._report_quality_issues(markdown) == []
