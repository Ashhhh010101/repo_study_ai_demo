from app.db.session import Base, engine


def init_db() -> None:
    from app.core.config import get_settings
    get_settings().database_url
    Base.metadata.create_all(bind=engine)
