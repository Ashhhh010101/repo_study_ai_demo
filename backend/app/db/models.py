from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.session import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RepoProject(Base, TimestampMixin):
    __tablename__ = "repo_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    repo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    repo_name: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[str | None] = mapped_column(String(255))
    local_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    files: Mapped[list["RepoFile"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    chunks: Mapped[list["CodeChunk"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    analysis: Mapped["RepoAnalysis | None"] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class RepoFile(Base, TimestampMixin):
    __tablename__ = "repo_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("repo_projects.id"), index=True)
    path: Mapped[str] = mapped_column(String(1000), nullable=False)
    language: Mapped[str | None] = mapped_column(String(100))
    file_type: Mapped[str | None] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, default=0)

    project: Mapped["RepoProject"] = relationship(back_populates="files")
    chunks: Mapped[list["CodeChunk"]] = relationship(
        back_populates="file", cascade="all, delete-orphan"
    )


class CodeChunk(Base, TimestampMixin):
    __tablename__ = "code_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("repo_projects.id"), index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("repo_files.id"), index=True)
    chunk_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    start_line: Mapped[int] = mapped_column(Integer, default=1)
    end_line: Mapped[int] = mapped_column(Integer, default=1)
    embedding_key: Mapped[str | None] = mapped_column(String(255))

    project: Mapped["RepoProject"] = relationship(back_populates="chunks")
    file: Mapped["RepoFile"] = relationship(back_populates="chunks")


class RepoAnalysis(Base, TimestampMixin):
    __tablename__ = "repo_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("repo_projects.id"), unique=True, index=True
    )
    overview: Mapped[str] = mapped_column(Text, default="")
    tech_stack_json: Mapped[dict] = mapped_column(JSON, default=dict)
    architecture_summary: Mapped[str] = mapped_column(Text, default="")
    folder_summary_json: Mapped[dict] = mapped_column(JSON, default=dict)
    important_files_json: Mapped[list] = mapped_column(JSON, default=list)
    request_flow: Mapped[str] = mapped_column(Text, default="")
    data_flow: Mapped[str] = mapped_column(Text, default="")
    setup_instructions: Mapped[str] = mapped_column(Text, default="")
    reading_order_json: Mapped[list] = mapped_column(JSON, default=list)
    risks: Mapped[str] = mapped_column(Text, default="")
    generated_report_markdown: Mapped[str] = mapped_column(Text, default="")

    project: Mapped["RepoProject"] = relationship(back_populates="analysis")


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("repo_projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), default="Default Session")

    project: Mapped["RepoProject"] = relationship(back_populates="chat_sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    used_chunks_json: Mapped[list] = mapped_column(JSON, default=list)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
