from sqlalchemy import inspect, text

from app.db.session import Base, engine


def init_db() -> None:
    from app.core.config import get_settings
    get_settings().database_url
    Base.metadata.create_all(bind=engine)
    columns = {column["name"] for column in inspect(engine).get_columns("repo_projects")}
    if "access_token_hash" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE repo_projects ADD COLUMN access_token_hash VARCHAR(64)")
            )
