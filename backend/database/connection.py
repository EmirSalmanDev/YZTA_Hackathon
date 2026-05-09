from collections.abc import Generator
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


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    create_db_and_tables()
    print("smoke ok")
