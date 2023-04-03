import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import sessionmaker

DB_DSN = os.getenv(
    "DB_DSN",
    "postgresql://postgres:password@localhost:5432/pytest_sqlalchemy_session_test",
)


def get_db_dsn() -> URL:
    dsn = make_url(DB_DSN)
    return dsn


engine = create_engine(url=get_db_dsn())

session_factory = sessionmaker(engine)
