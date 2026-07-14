FILE_SUMMARY_PROMPT = """You are analyzing a repository file.
Return JSON with keys: purpose, key_responsibilities, important_symbols, dependencies, notes.
Use only the provided content. If something is uncertain, say so clearly.

File path: {file_path}
Language: {language}

Content:
{content}
"""

FOLDER_SUMMARY_PROMPT = """You are summarizing a repository folder.
Return JSON with keys: folder_purpose, modules, important_files, how_it_fits.
Use only the provided evidence.

Folder path: {folder_path}
Files:
{files}

File summaries:
{file_summaries}
"""

ARCHITECTURE_REPORT_PROMPT = """You are writing a structured repository onboarding report.
Use only the provided repository context. Do not hallucinate missing features.
Separate confirmed facts from inferred points where useful. Always reference file paths.
If context is missing, say so explicitly.

Repository context:
{context}

Return markdown with these sections:
1. Project Overview
2. Tech Stack
3. How To Run Locally
4. Folder-by-Folder Explanation
5. Important Files
6. Backend Flow
7. Frontend Flow
8. Database Flow
9. Authentication Flow if found
10. External Services if found
11. Architecture Summary
12. Recommended Reading Order
13. Risks / Unknowns
14. Developer Onboarding Notes
"""

REPO_QA_PROMPT = """You are answering a question about a code repository.
Use the final report summary and retrieved chunks. Prefer direct code evidence.
If the answer is unclear, say what is missing. Cite file paths and line numbers when possible.

Question:
{question}

Report summary:
{report_summary}

Retrieved chunks:
{retrieved_chunks}

Chat history summary:
{chat_history}

Format:
- Direct answer
- Relevant files
- Explanation
- If unclear, say what is missing
"""
