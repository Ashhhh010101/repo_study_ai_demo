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
        "folder_purpose": responsibilities[0] if responsibilities else "Not enough context.",
        "modules": [item["path"] for item in file_summaries[:8]],
        "important_files": [item["path"] for item in important_files],
        "how_it_fits": f"Contains {len(file_summaries)} scanned files under {folder_path}.",
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


def derive_report_fields(markdown_report: str, stack: dict, folder_summaries: dict, important_files: list[dict]) -> dict:
    reading_order = [{"path": item["path"], "why": "High-signal entry point or core module"} for item in important_files[:8]]
    return {
        "overview": markdown_report.split("\n", 8)[0].replace("#", "").strip(),
        "tech_stack_json": stack,
        "architecture_summary": "See generated markdown report for the consolidated architecture summary.",
        "folder_summary_json": folder_summaries,
        "important_files_json": important_files[:12],
        "request_flow": "See Backend Flow and Frontend Flow sections in the generated report.",
        "data_flow": "See Database Flow and architecture sections in the generated report.",
        "setup_instructions": "See How To Run Locally section in the generated report.",
        "reading_order_json": reading_order,
        "risks": "Review the Risks / Unknowns section in the generated report.",
        "generated_report_markdown": markdown_report,
    }


def build_basic_markdown_report(
    repo_name: str,
    stack: dict,
    important_files: list[dict],
    folder_summaries: dict,
) -> str:
    folders_markdown = "\n".join(
        f"- `{folder}`: {summary.get('folder_purpose', 'Not enough context.')}"
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

## 3. How To Run Locally
Inferred: Review README and package/dependency files for exact commands.

## 4. Folder-by-Folder Explanation
{folders_markdown or "- Not enough context."}

## 5. Important Files
{important_markdown or "- Not enough context."}

## 6. Backend Flow
Inferred from file layout and important modules.

## 7. Frontend Flow
Inferred from file layout and important modules.

## 8. Database Flow
State database-related files if present; otherwise insufficient context.

## 9. Authentication Flow if found
No confirmed authentication flow found unless auth files were detected.

## 10. External Services if found
No confirmed external service list beyond detected config and code references.

## 11. Architecture Summary
This report should be refined by the LLM when available; otherwise it remains a grounded structural summary.

## 12. Recommended Reading Order
{important_markdown or "- Start with README.md if present."}

## 13. Risks / Unknowns
This local fallback report avoids guessing when file evidence is limited.

## 14. Developer Onboarding Notes
Start from README, entrypoints, config, routes/services, and core domain modules.
"""
