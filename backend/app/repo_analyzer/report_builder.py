import json
from collections import defaultdict


def summarize_folder_from_files(folder_path: str, file_summaries: list[dict]) -> dict:
    important_files = sorted(
        file_summaries, key=lambda item: item.get("importance_score", 0), reverse=True
    )[:5]
    responsibilities = []
    for item in file_summaries[:8]:
        purpose = item.get("summary_json", {}).get("purpose")
        if purpose:
            responsibilities.append(f"{item['path']}: {purpose}")
    return {
        "folder_purpose": responsibilities[0] if responsibilities else "No file summary established this folder's purpose.",
        "modules": [item["path"] for item in file_summaries[:8]],
        "important_files": [item["path"] for item in important_files],
        "how_it_fits": f"Contains {len(file_summaries)} scanned files under {folder_path}.",
        "confidence": "low",
        "evidence": [item["path"] for item in important_files],
    }


def build_report_context(
    repo_name: str,
    stack: dict,
    file_tree: list[dict],
    important_files: list[dict],
    folder_summaries: dict,
    readme_summary: dict | None,
) -> str:
    payload = {
        "repo_name": repo_name,
        "stack": stack,
        "file_tree": file_tree,
        "important_files": important_files,
        "folder_summaries": folder_summaries,
        "readme_summary": readme_summary or {},
    }
    return json.dumps(payload, indent=2)


def _section(markdown_report: str, heading: str, fallback: str) -> str:
    """Extract a numbered markdown section without exposing UI placeholder text."""
    lines = markdown_report.splitlines()
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.strip().lstrip("#").strip().lower().startswith(heading.lower())
        ),
        None,
    )
    if start is None:
        return fallback

    content: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("## ") or line.startswith("# "):
            break
        content.append(line)
    value = "\n".join(content).strip()
    return value or fallback


def derive_report_fields(markdown_report: str, stack: dict, folder_summaries: dict, important_files: list[dict]) -> dict:
    reading_order = [{"path": item["path"], "why": "High-signal entry point or core module"} for item in important_files[:8]]
    overview = _section(markdown_report, "1. Project Overview", "The report did not contain a project overview.")
    architecture = _section(markdown_report, "4. Runtime Architecture and Component Responsibilities", "The report did not contain a runtime architecture section.")
    request_flow = _section(markdown_report, "5. End-to-End Request and Data Flows", "The report did not contain a request and data flow section.")
    data_flow = _section(markdown_report, "8. Data Model, Persistence, Caching, and Indexing", "The report did not contain a data and persistence section.")
    setup = _section(markdown_report, "16. How To Run Locally", "The report did not contain local run instructions.")
    risks = _section(markdown_report, "18. Risks, Trade-offs, and Unknowns", "The report did not contain a risks and unknowns section.")
    return {
        "overview": overview,
        "tech_stack_json": stack,
        "architecture_summary": architecture,
        "folder_summary_json": folder_summaries,
        "important_files_json": important_files[:12],
        "request_flow": request_flow,
        "data_flow": data_flow,
        "setup_instructions": setup,
        "reading_order_json": reading_order,
        "risks": risks,
        "generated_report_markdown": markdown_report,
    }


def build_basic_markdown_report(
    repo_name: str,
    stack: dict,
    important_files: list[dict],
    folder_summaries: dict,
) -> str:
    folders_markdown = "\n".join(
        f"- `{folder}`: {summary.get('folder_purpose', 'No folder purpose was established from scanned files.')}"
        for folder, summary in folder_summaries.items()
    )
    important_markdown = "\n".join(
        f"- `{item['path']}`"
        for item in important_files[:10]
    )
    return f"""# {repo_name}

## 1. Project Overview
Confirmed from code: The repository was analyzed from its current file tree and important files.

## 2. Tech Stack
Confirmed from code: {json.dumps(stack)}

## 3. System Context and Actors
Confirmed actors and boundaries could not be fully established without a provider response; review the important files below.

## 4. Runtime Architecture and Component Responsibilities
The scanner identified the important modules below, but a complete runtime relationship map was not produced.

## 5. End-to-End Request and Data Flows
No end-to-end request flow was confirmed by the local fallback.

## 6. Frontend Architecture and State Flow
Review detected frontend entrypoints and the important-file list when present.

## 7. Backend/API Architecture
Review detected backend entrypoints, routes, and services when present.

## 8. Data Model, Persistence, Caching, and Indexing
Review detected database, storage, and indexing files when present.

## 9. Integration and External Service Boundaries
No complete integration map was confirmed by the local fallback.

## 10. Authentication, Authorization, Secrets, and Threat Model
No authentication or authorization behavior was confirmed by the local fallback.

## 11. Reliability, Concurrency, Failure Handling, and Recovery
No complete reliability analysis was produced by the local fallback.

## 12. Scalability and Performance Considerations
Repository size and detected stack are available, but runtime scaling behavior was not confirmed.

## 13. Deployment, Configuration, and Operations
Review README and dependency/configuration files for repository-specific commands and environment variables.

## 14. Important Production Files (with why each matters)
{important_markdown or "- No important files were identified by the scanner."}

## 15. Folder-by-Folder Explanation
{folders_markdown or "- No folder summaries were produced from the scanned files."}

## 16. How To Run Locally
Review README and package/dependency files for exact commands; the local fallback does not infer commands.

## 17. Recommended Reading Order
{important_markdown or "- Start with README.md if present."}

## 18. Risks, Trade-offs, and Unknowns
The provider report was unavailable or failed validation, so runtime relationships remain unconfirmed.

## 19. Developer Onboarding Notes
Start from README, entrypoints, config, routes/services, and core domain modules.
"""
