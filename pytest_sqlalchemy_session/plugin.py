import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser

from pytest_sqlalchemy_session.fixtures import (  # noqa
    _auto_mock_session_by_marker,
    _db,
    _session,
    _strict_session_rule,
    db_session,
    mock_session,
)


@pytest.hookimpl
def pytest_addoption(parser: Parser) -> None:
    parser.addini(
        "strict-db",
        type="bool",
        help="Enable strict DB mode. Should use marker sqlalchemy_db in all tests that use DB session.",
        default=False,
    )


@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config) -> None:
    config._enable_strict = config.getini("strict-db")  # type: ignore

    config.addinivalue_line(
        "markers", "sqlalchemy_db: mark test to use isolated transactions"
    )
    config.addinivalue_line(
        "markers", "transactional_db: mark test to use usual transactions"
    )
