import contextlib
import typing
from typing import Callable, Generator, Tuple

import pytest
from pytest import Config, FixtureRequest, UsageError
from pytest_mock import MockFixture
from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine, RootTransaction
from sqlalchemy.orm import Session, SessionTransaction, sessionmaker
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.compiler import Compiled

from pytest_sqlalchemy_session.session import TestSession

DbType = Tuple[sessionmaker, Engine]
EventClauseElement = typing.Union[ClauseElement, Compiled, str]


class RestartSavepoint:
    def __init__(
        self,
        root_transaction: RootTransaction,
        main_nested_transaction: SessionTransaction,
    ):
        self.main_nested_transaction = main_nested_transaction
        self.root_transaction = root_transaction

    def __call__(self, session: Session, trans: SessionTransaction):
        if self.root_transaction.is_active and (
            getattr(
                trans, "fake_nested", None
            )  # need to recreate main nested transaction after Session.begin()
            or (
                trans == self.main_nested_transaction
            )  # need to recreate main nested transaction after close
        ):
            # ensure that state is expired the way
            # session.commit() at the top level normally does
            session.expire_all()

            if (
                session._trans_context_manager == trans
                and session._trans_context_manager._transaction_is_closed()
            ):
                session._trans_context_manager = trans.parent

            new_nested_transaction = session.begin_nested()
            self.main_nested_transaction = new_nested_transaction


@contextlib.contextmanager
def modify_transaction_to_rollback(  # noqa: C901
    db: DbType,
) -> Generator[Tuple[Connection, RootTransaction, Session], None, None]:
    """
    Create a transactional context for tests to run in.
    """

    # Start a transaction
    _session_factory, engine = db
    connection = engine.connect()
    root_transaction = connection.begin()

    session_factory = sessionmaker(**_session_factory.kw, class_=TestSession)

    session = session_factory()

    # Make sure the session can't be closed by accident in the codebase
    session_force_close = session.close

    def close() -> None:
        session.rollback()

    session.close = close

    # Begin a nested transaction (any new transactions created in the codebase
    # will be held until this outer transaction is committed or closed)
    main_nested_transaction = session.begin_nested()
    # Each time the SAVEPOINT for the nested transaction ends, reopen it

    restart_savepoint = RestartSavepoint(
        root_transaction=root_transaction,
        main_nested_transaction=main_nested_transaction,
    )

    event.listens_for(session, "after_transaction_end")(restart_savepoint)

    try:
        yield connection, root_transaction, session
    finally:
        event.remove(session, "after_transaction_end", restart_savepoint)
        # Rollback the transaction and return the connection to the pool
        session_force_close()
        root_transaction.rollback()
        connection.close()


@pytest.fixture(scope="session")
def _db() -> DbType:
    """
    A user-defined _db fixture is required to provide the plugin with a SQLAlchemy
    Session object that can access the test database. If the user hasn't defined
    that fixture, raise an error.
    """
    msg = (
        "_db fixture not defined. The pytest-sqlalchemy-session plugin "
        "requires you to define a _db fixture that returns a session factory and engine "
        "with access to your test database. For more information, see the plugin "
        "documentation."
    )

    raise NotImplementedError(msg)


@pytest.fixture(scope="function", autouse=True)
def _strict_session_rule(
    pytestconfig: Config, request: FixtureRequest, _db: DbType
) -> None:
    enable_strict = pytestconfig._enable_strict  # type: ignore
    session_factory, engine = _db
    transactional_marker = request.node.get_closest_marker("transactional_db")

    if not enable_strict or transactional_marker:
        return

    db_marker = request.node.get_closest_marker("sqlalchemy_db")

    if db_marker:
        return

    @event.listens_for(engine, "before_execute")
    def raise_error_in_strict_mode(*args, **kwargs) -> None:
        raise UsageError(
            "The pytest.mark.sqlalchemy_db or pytest.mark.transactional_db marker is required to execute db queries."
        )

    request.addfinalizer(
        lambda: event.remove(engine, "before_execute", raise_error_in_strict_mode)
    )


@pytest.fixture(scope="function")
def _session(_db: DbType) -> Generator[Session, None, None]:
    with modify_transaction_to_rollback(_db) as db:
        _, _, session = db
        yield session


@pytest.fixture(scope="function", autouse=True)
def _auto_mock_session_by_marker(
    request: FixtureRequest,
    _session: Session,
    mock_session: Callable[[Session], Session],
) -> None:
    if request.node.get_closest_marker("sqlalchemy_db"):
        mock_session(_session)


@pytest.fixture(scope="function")
def mock_session(
    pytestconfig: Config, mocker: MockFixture
) -> Callable[[Session], Session]:
    def _mock_session(session: Session) -> Session:
        mocker.patch.object(sessionmaker, "__call__", return_value=session)

        return session

    return _mock_session


@pytest.fixture(scope="function")
def db_session(
    _session: Session, mock_session: Callable[[Session], Session]
) -> Session:
    """
    Make sure all the different ways that we access the database in the code
    are scoped to a transactional context, and return a Session object that
    can interact with the database in the tests.

    Use this fixture in tests when you would like to use the SQLAlchemy ORM
    API, just as you might use a SQLAlchemy Session object.
    """
    return _session
