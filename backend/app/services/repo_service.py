import logging
import time
from pydantic import SecretStr
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import models
from app.repo_analyzer.chunker import chunk_file
from app.repo_analyzer.cloner import (
    CloneError,
    clone_public_repo,
    validate_branch_name,
    validate_github_url,
)
from app.repo_analyzer.context_builder import build_file_tree
from app.repo_analyzer.importance_ranker import rank_files
from app.repo_analyzer.scanner import ScanLimitError, scan_repository
from app.repo_analyzer.stack_detector import detect_stack
from app.services.embedding_service import EmbeddingService
from app.services.report_service import ReportService
from app.storage.local_repo_store import LocalRepoStore


class RepoService:
    def __init__(
        self,
        local_repo_store: LocalRepoStore | None = None,
        report_service: ReportService | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.local_repo_store = local_repo_store or LocalRepoStore()
        self.report_service = report_service or ReportService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)

    def _set_status(self, db: Session, project: models.RepoProject, status: str, error_message: str | None = None) -> None:
        project.status = status
        project.error_message = error_message
        db.add(project)
        db.commit()
        db.refresh(project)

    def analyze_repository(
        self,
        db: Session,
        repo_url: str,
        branch: str | None,
        commit: str | None,
        gemini_api_key: SecretStr,
        model: str | None = None,
        provider: str = "gemini",
    ) -> tuple[models.RepoProject, models.RepoAnalysis]:
        owner, repo_name = validate_github_url(repo_url)
        branch = validate_branch_name(branch)
        commit = commit.lower() if commit else None
        if model is not None and model not in self.settings.supported_gemini_models:
            raise CloneError("The selected AI model is not supported by this deployment.")
        self.report_service.model = model
        self.report_service.provider = provider
        canonical_repo_url = f"https://github.com/{owner}/{repo_name}"
        project = models.RepoProject(
            repo_url=canonical_repo_url,
            repo_name=repo_name,
            branch=branch,
            commit=commit,
            local_path="",
            status="pending",
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        self.logger.info("Analysis project created project_id=%s repo=%s", project.id, repo_name)

        try:
            self._set_status(db, project, "cloning")
            step_started = time.perf_counter()
            self.logger.info("analysis.step project_id=%s step=clone status=start", project.id)
            cache_key = self.local_repo_store.get_repo_key(canonical_repo_url, branch, commit)
            local_path = self.local_repo_store.get_repo_path(canonical_repo_url, branch, commit)
            with self.local_repo_store.lock_for(cache_key):
                clone_public_repo(canonical_repo_url, local_path, branch=branch, commit=commit, timeout_seconds=self.settings.clone_timeout_seconds)
                self.local_repo_store.write_metadata(local_path, canonical_repo_url, branch, commit)
            self.logger.info("analysis.step project_id=%s step=clone status=complete duration_ms=%.1f", project.id, (time.perf_counter() - step_started) * 1000)
            project.local_path = str(local_path)
            db.add(project)
            db.commit()
            db.refresh(project)

            self._set_status(db, project, "scanning")
            step_started = time.perf_counter()
            self.logger.info("analysis.step project_id=%s step=scan status=start", project.id)
            scanned_files = scan_repository(
                local_path,
                max_file_size_bytes=self.settings.max_file_size_bytes,
                max_files=self.settings.max_scanned_files,
                max_total_bytes=self.settings.max_total_scan_bytes,
            )
            ranked_files = rank_files(scanned_files)
            self.logger.info("Repository scanned project_id=%s files=%s", project.id, len(ranked_files))
            self.logger.info("analysis.step project_id=%s step=scan status=complete duration_ms=%.1f", project.id, (time.perf_counter() - step_started) * 1000)
            stack = detect_stack(ranked_files)
            file_tree = build_file_tree(ranked_files)

            db.query(models.RepoFile).filter(models.RepoFile.project_id == project.id).delete()
            db.query(models.CodeChunk).filter(models.CodeChunk.project_id == project.id).delete()
            db.query(models.RepoAnalysis).filter(models.RepoAnalysis.project_id == project.id).delete()
            db.commit()
            file_records_by_path: dict[str, models.RepoFile] = {}
            for file_metadata in ranked_files:
                file_record = models.RepoFile(
                    project_id=project.id,
                    path=file_metadata["path"],
                    language=file_metadata["language"],
                    file_type=file_metadata["file_type"],
                    size_bytes=file_metadata["size_bytes"],
                    content_hash=file_metadata["content_hash"],
                    importance_score=file_metadata["importance_score"],
                )
                db.add(file_record)
                db.flush()
                file_records_by_path[file_metadata["path"]] = file_record
            db.commit()
            self.logger.info("analysis.step project_id=%s step=persist_files status=complete files=%s", project.id, len(file_records_by_path))

            self._set_status(db, project, "indexing")
            step_started = time.perf_counter()
            self.logger.info("analysis.step project_id=%s step=index status=start", project.id)
            chunk_payloads: list[dict] = []
            for file_metadata in ranked_files:
                file_record = file_records_by_path[file_metadata["path"]]
                for chunk in chunk_file(file_metadata, max_chars=self.settings.max_chunk_chars):
                    chunk_record = models.CodeChunk(
                        project_id=project.id,
                        file_id=file_record.id,
                        chunk_type=chunk["chunk_type"],
                        content=chunk["content"],
                        start_line=chunk["start_line"],
                        end_line=chunk["end_line"],
                        embedding_key=f"{project.id}:{file_record.id}:{chunk['start_line']}",
                    )
                    db.add(chunk_record)
                    db.flush()
                    chunk_payloads.append(
                        {
                            "chunk_id": chunk_record.id,
                            "file_path": file_metadata["path"],
                            "chunk_type": chunk["chunk_type"],
                            "content": chunk["content"],
                            "start_line": chunk["start_line"],
                            "end_line": chunk["end_line"],
                        }
                    )
            db.commit()
            self.embedding_service.index_project_chunks(project.id, chunk_payloads)
            self.logger.info("Repository indexed project_id=%s chunks=%s", project.id, len(chunk_payloads))
            self.logger.info("analysis.step project_id=%s step=index status=complete duration_ms=%.1f", project.id, (time.perf_counter() - step_started) * 1000)

            self._set_status(db, project, "analyzing")
            self.logger.info("analysis.step project_id=%s step=file_summaries status=start files=%s", project.id, len(ranked_files[:12]))
            important_files = ranked_files[:12]
            file_summaries = self.report_service.summarize_files(important_files, gemini_api_key)
            self.logger.info("analysis.step project_id=%s step=file_summaries status=complete", project.id)
            folder_summaries = self.report_service.summarize_folders(file_summaries, gemini_api_key)
            self.logger.info("analysis.step project_id=%s step=folder_summaries status=complete folders=%s", project.id, len(folder_summaries))
            readme_summary = next(
                (item["summary_json"] for item in file_summaries if item["path"].lower() == "readme.md"),
                None,
            )
            report_fields = self.report_service.generate_repo_report(
                repo_name=repo_name,
                stack=stack,
                file_tree=file_tree,
                important_files=[
                    {
                        "path": item["path"],
                        "importance_score": item["importance_score"],
                        "summary": item["summary_json"],
                    }
                    for item in file_summaries
                ],
                folder_summaries=folder_summaries,
                readme_summary=readme_summary,
                gemini_api_key=gemini_api_key,
            )
            self.logger.info("analysis.step project_id=%s step=architecture_report status=complete", project.id)

            analysis = models.RepoAnalysis(project_id=project.id, **report_fields)
            db.add(analysis)
            db.commit()
            db.refresh(analysis)

            self._set_status(db, project, "completed")
            self.logger.info("Analysis completed project_id=%s", project.id)
            return project, analysis
        except Exception as exc:
            self.logger.exception("Analysis failed project_id=%s", project.id)
            if isinstance(exc, (CloneError, ScanLimitError)):
                safe_error = str(exc)
            else:
                safe_error = "Repository analysis failed. Review the backend logs for details."
            self._set_status(db, project, "failed", safe_error)
            raise
