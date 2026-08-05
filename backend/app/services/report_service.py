import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from pydantic import BaseModel, SecretStr, ValidationError

from app.core.config import get_settings
from app.repo_analyzer.prompt_manager import (
    ARCHITECTURE_REPORT_PROMPT,
    FILE_SUMMARY_PROMPT,
    FOLDER_SUMMARY_PROMPT,
    JSON_REPAIR_PROMPT,
    REPORT_REPAIR_PROMPT,
)
from app.schemas.analysis import FileSummary, FolderSummary
from app.repo_analyzer.report_builder import (
    build_basic_markdown_report,
    build_report_context,
    derive_report_fields,
    summarize_folder_from_files,
)
from app.services.llm_service import LLMService

_SUMMARY_CACHE: dict[tuple[str, str, str, str], dict] = {}
_SUMMARY_CACHE_LOCK = Lock()


class ReportService:
    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or LLMService()
        self.settings = get_settings()
        self.model: str | None = None
        self.provider = "gemini"

    @staticmethod
    def _parse_json(raw: str, schema: type[BaseModel]) -> dict:
        candidate = raw.strip()
        if candidate.startswith("```"):
            lines = candidate.splitlines()
            candidate = "\n".join(lines[1:-1]).strip()
        return schema.model_validate(json.loads(candidate)).model_dump()

    def _generate_validated_json(
        self,
        prompt: str,
        schema: type[BaseModel],
        api_key: SecretStr,
    ) -> dict:
        raw = self.llm_service.generate_text(
            prompt, api_key, "application/json", self.model, self.provider
        )
        try:
            return self._parse_json(raw, schema)
        except (json.JSONDecodeError, ValidationError):
            repair_prompt = JSON_REPAIR_PROMPT.format(
                schema=json.dumps(schema.model_json_schema(), indent=2),
                candidate=raw[:12_000],
            )
            repaired = self.llm_service.generate_text(
                repair_prompt, api_key, "application/json", self.model, self.provider
            )
            return self._parse_json(repaired, schema)

    def summarize_file(self, file_metadata: dict, gemini_api_key: SecretStr) -> dict:
        default_models = {
            "gemini": self.settings.gemini_model,
            "openai": "gpt-5.2",
            "anthropic": "claude-sonnet-4-20250514",
        }
        cache_key = (
            self.provider,
            self.model or default_models[self.provider],
            file_metadata["path"],
            file_metadata["content_hash"],
        )
        with _SUMMARY_CACHE_LOCK:
            cached = _SUMMARY_CACHE.get(cache_key)
        if cached is not None:
            return cached.copy()

        prompt = FILE_SUMMARY_PROMPT.format(
            file_path=file_metadata["path"],
            language=file_metadata["language"],
            content=file_metadata["content"][:8000],
        )
        try:
            summary = self._generate_validated_json(prompt, FileSummary, gemini_api_key)
            if self.settings.summary_cache_entries:
                with _SUMMARY_CACHE_LOCK:
                    _SUMMARY_CACHE[cache_key] = summary
                    while len(_SUMMARY_CACHE) > self.settings.summary_cache_entries:
                        _SUMMARY_CACHE.pop(next(iter(_SUMMARY_CACHE)))
            return summary.copy()
        except Exception:
            return {
                "purpose": "Summary unavailable; fallback summary generated locally.",
                "key_responsibilities": [],
                "important_symbols": [],
                "dependencies": [],
                "notes": "LLM summary failed or returned invalid JSON.",
                "confidence": "low",
                "evidence": [file_metadata["path"]],
            }

    def summarize_files(self, files: list[dict], gemini_api_key: SecretStr) -> list[dict]:
        max_workers = min(self.settings.analysis_max_workers, len(files))
        if max_workers <= 1:
            return [
                {
                    "path": file_metadata["path"],
                    "importance_score": file_metadata["importance_score"],
                    "summary_json": self.summarize_file(file_metadata, gemini_api_key),
                }
                for file_metadata in files
            ]

        results: list[dict | None] = [None] * len(files)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(self.summarize_file, file_metadata, gemini_api_key): index
                for index, file_metadata in enumerate(files)
            }
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                file_metadata = files[index]
                results[index] = {
                    "path": file_metadata["path"],
                    "importance_score": file_metadata["importance_score"],
                    "summary_json": future.result(),
                }
        return [result for result in results if result is not None]

    def summarize_folders(self, file_summaries: list[dict], gemini_api_key: SecretStr) -> dict:
        folders: dict[str, list[dict]] = defaultdict(list)
        for item in file_summaries:
            folder = item["path"].rsplit("/", 1)[0] if "/" in item["path"] else "."
            folders[folder].append(item)

        def summarize_folder(folder_path: str, items: list[dict]) -> tuple[str, dict]:
            prompt = FOLDER_SUMMARY_PROMPT.format(
                folder_path=folder_path,
                files="\n".join(item["path"] for item in items),
                file_summaries=json.dumps(
                    [
                        {
                            "path": item["path"],
                            "summary": item["summary_json"],
                        }
                        for item in items[:10]
                    ],
                    indent=2,
                ),
            )
            try:
                return folder_path, self._generate_validated_json(
                    prompt, FolderSummary, gemini_api_key
                )
            except Exception:
                return folder_path, summarize_folder_from_files(folder_path, items)

        results = {}
        folder_items = list(folders.items())
        max_workers = min(self.settings.analysis_max_workers, len(folder_items))
        if max_workers <= 1:
            for folder_path, items in folder_items:
                result_path, result = summarize_folder(folder_path, items)
                results[result_path] = result
            return results

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(summarize_folder, folder_path, items)
                for folder_path, items in folder_items
            ]
            for future in as_completed(futures):
                folder_path, result = future.result()
                results[folder_path] = result
        return results

    def generate_repo_report(
        self,
        repo_name: str,
        stack: dict,
        file_tree: list[dict],
        important_files: list[dict],
        folder_summaries: dict,
        readme_summary: dict | None,
        gemini_api_key: SecretStr,
    ) -> dict:
        context = build_report_context(
            repo_name=repo_name,
            stack=stack,
            file_tree=file_tree,
            important_files=important_files,
            folder_summaries=folder_summaries,
            readme_summary=readme_summary,
        )
        prompt = ARCHITECTURE_REPORT_PROMPT.format(context=context)
        try:
            markdown = self.llm_service.generate_text(prompt, gemini_api_key, model=self.model, provider=self.provider)
            issues = self._report_quality_issues(markdown)
            if issues:
                markdown = self.llm_service.generate_text(
                    REPORT_REPAIR_PROMPT.format(
                        issues=", ".join(issues),
                        context=context,
                        draft=markdown[:40_000],
                    ),
                    gemini_api_key,
                    model=self.model,
                    provider=self.provider,
                )
                if self._report_quality_issues(markdown):
                    raise ValueError("The repaired report did not pass quality checks.")
        except Exception:
            markdown = build_basic_markdown_report(repo_name, stack, important_files, folder_summaries)
        return derive_report_fields(markdown, stack, folder_summaries, important_files)

    @staticmethod
    def _report_quality_issues(markdown: str) -> list[str]:
        required = [
            "Project Overview", "Tech Stack", "System Context and Actors",
            "Runtime Architecture and Component Responsibilities",
            "End-to-End Request and Data Flows", "Frontend Architecture and State Flow",
            "Backend/API Architecture", "Data Model, Persistence, Caching, and Indexing",
            "Integration and External Service Boundaries",
            "Authentication, Authorization, Secrets, and Threat Model",
            "Reliability, Concurrency, Failure Handling, and Recovery",
            "Scalability and Performance Considerations",
            "Deployment, Configuration, and Operations",
            "Important Production Files", "Folder-by-Folder Explanation",
            "How To Run Locally", "Recommended Reading Order",
            "Risks, Trade-offs, and Unknowns", "Developer Onboarding Notes",
        ]
        issues = [
            f"missing section {index}. {title}"
            for index, title in enumerate(required, start=1)
            if f"{index}. {title}" not in markdown
        ]
        lowered = markdown.lower()
        for placeholder in ("tbd", "todo", "add details here", "see generated report"):
            if placeholder in lowered:
                issues.append(f"placeholder phrase: {placeholder}")
        if len(markdown.strip()) < 1_000:
            issues.append("report is too short")
        return issues
