import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from pydantic import SecretStr

from app.core.config import get_settings
from app.repo_analyzer.prompt_manager import (
    ARCHITECTURE_REPORT_PROMPT,
    FILE_SUMMARY_PROMPT,
    FOLDER_SUMMARY_PROMPT,
)
from app.repo_analyzer.report_builder import (
    build_basic_markdown_report,
    build_report_context,
    derive_report_fields,
    summarize_folder_from_files,
)
from app.services.llm_service import LLMService


class ReportService:
    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or LLMService()
        self.settings = get_settings()

    def summarize_file(self, file_metadata: dict, gemini_api_key: SecretStr) -> dict:
        prompt = FILE_SUMMARY_PROMPT.format(
            file_path=file_metadata["path"],
            language=file_metadata["language"],
            content=file_metadata["content"][:8000],
        )
        try:
            raw = self.llm_service.generate_text(prompt, gemini_api_key, "application/json")
            return json.loads(raw)
        except Exception:
            return {
                "purpose": "Summary unavailable; fallback summary generated locally.",
                "key_responsibilities": [],
                "important_symbols": [],
                "dependencies": [],
                "notes": "LLM summary failed or returned invalid JSON.",
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
                raw = self.llm_service.generate_text(prompt, gemini_api_key, "application/json")
                return folder_path, json.loads(raw)
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
            markdown = self.llm_service.generate_text(prompt, gemini_api_key)
        except Exception:
            markdown = build_basic_markdown_report(repo_name, stack, important_files, folder_summaries)
        return derive_report_fields(markdown, stack, folder_summaries, important_files)
