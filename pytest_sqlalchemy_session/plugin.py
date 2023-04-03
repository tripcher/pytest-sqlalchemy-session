import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser

from pytest_sqlalchemy_session.fixtures import (  # noqa
    _db,
    _session,
    _transaction,
    db_session,
)


@pytest.hookimpl
def pytest_addoption(parser: Parser) -> None:
    base_msg = (
        "A whitespace-separated list of {obj} objects that should be mocked."
        + "Each instance should be formatted as a standard "
        + "Python import path. Useful for mocking global objects that are "
        + "imported throughout your app's internal code."
    )

    parser.addini(
        "mocked-sessions", type="args", help=base_msg.format(obj="SQLAlchemy Session")
    )

    parser.addini(
        "mocked-sessionmakers",
        type="args",
        help=base_msg.format(obj="SQLAlchemy Sessionmaker"),
    )


@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config) -> None:
    config._mocked_sessions = config.getini("mocked-sessions")  # type: ignore
    config._mocked_sessionmakers = config.getini("mocked-sessionmakers")  # type: ignore
