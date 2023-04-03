import typing

import pytest
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from pytest_sqlalchemy_session_test.app.db import engine, get_db_dsn, session_factory
from pytest_sqlalchemy_session_test.app.tables import metadata

pytest_plugins = ["pytest_sqlalchemy_session.plugin"]


@pytest.fixture(scope="session")
def db_dsn() -> URL:
    return get_db_dsn()


@pytest.fixture(scope="session")
def database(db_dsn: URL):
    if not database_exists(db_dsn):
        create_database(db_dsn)

    with engine.begin() as connection:
        metadata.create_all(connection)

    yield

    with engine.begin() as connection:
        metadata.drop_all(connection)

    if database_exists(db_dsn):
        drop_database(db_dsn)


@pytest.fixture(scope="session")
def _db(database) -> typing.Tuple[sessionmaker, Engine]:
    """Necessary for pytest-sqlalchemy-session plugin."""
    return session_factory, engine
