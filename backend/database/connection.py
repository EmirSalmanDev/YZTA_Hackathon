from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

_DB_DIR = Path("data")
_DB_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{_DB_DIR / 'kobi.db'}"

# check_same_thread=False is required for SQLite when used with FastAPI's
# async request handling, which may run sync DB calls across threads.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def _warn_if_stale_schema() -> None:
    """Warn once at startup if the on-disk DB has the old Product column names."""
    if not (_DB_DIR / "kobi.db").exists():
        return
    from sqlalchemy import inspect as sa_inspect
    inspector = sa_inspect(engine)
    if "product" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("product")}
    if columns & {"quantity", "threshold"}:
        import warnings
        warnings.warn(
            "Stale DB schema: 'product' table has old columns (quantity/threshold). "
            "Delete data/kobi.db and restart to apply the current schema.",
            UserWarning,
            stacklevel=2,
        )


def create_db_and_tables() -> None:
    _warn_if_stale_schema()
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for direct use in tools, memory, and helpers."""
    with Session(engine) as session:
        yield session


def get_session_dep() -> Generator[Session, None, None]:
    """Plain generator dependency for FastAPI's Depends()."""
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    create_db_and_tables()
    print("smoke ok")
