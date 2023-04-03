from typing import Any, Generator, Tuple

import pytest
from sqlalchemy.engine import Connection, Engine, RootTransaction
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Session, SessionTransaction, sessionmaker

from pytest_sqlalchemy_session.session import TestSession


@pytest.fixture(scope="session")
def _db() -> Tuple[sessionmaker, Engine]:
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


@pytest.fixture(scope="function")
def _transaction(
    _db: Tuple[sessionmaker, Engine]
) -> Generator[Tuple[Connection, RootTransaction, Session], None, None]:
    """
    Create a transactional context for tests to run in.
    """
    # Start a transaction
    _session_factory, engine = _db
    connection = engine.connect()
    root_transaction = connection.begin()

    session_factory = sessionmaker(**_session_factory.kw, class_=TestSession)

    session = session_factory()

    # Make sure the session, connection, and transaction can't be closed by accident in
    # the codebase
    connection_force_close = connection.close
    root_transaction_force_rollback = root_transaction.rollback
    session_force_close = session.close

    connection.close = lambda: None
    # main_transaction.rollback = lambda: None
    session.close = lambda: None

    # Begin a nested transaction (any new transactions created in the codebase
    # will be held until this outer transaction is committed or closed)
    session.begin_nested()

    # Each time the SAVEPOINT for the nested transaction ends, reopen it
    @listens_for(session, "after_transaction_end")
    def restart_savepoint(session: Session, trans: SessionTransaction) -> None:
        if root_transaction.is_active and (trans.nested and not trans._parent.nested):
            # ensure that state is expired the way
            # session.commit() at the top level normally does
            session.expire_all()

            session.begin_nested()

    # # Force the connection to use nested transactions
    # connection.begin = connection.begin_nested

    # If an object gets moved to the 'detached' state by a call to flush the session,
    # add it back into the session (this allows us to see changes made to objects
    # in the context of a test, even when the change was made elsewhere in
    # the codebase)
    @listens_for(session, "persistent_to_detached")
    @listens_for(session, "deleted_to_detached")
    def rehydrate_object(session: Session, obj: Any) -> None:
        session.add(obj)

    try:
        yield connection, root_transaction, session
    finally:
        # Rollback the transaction and return the connection to the pool
        session_force_close()
        root_transaction_force_rollback()
        connection_force_close()


@pytest.fixture(scope="function")
def _session(pytestconfig, _transaction, mocker) -> Session:
    """
    Mock out Session objects (a common way of interacting with the database using
    the SQLAlchemy ORM) using a transactional context.
    """
    _, _, session = _transaction

    # Whenever the code tries to access a global session, use the Session object instead
    for mocked_session in pytestconfig._mocked_sessions:
        mocker.patch(mocked_session, new=session)

    # Mock sessionmaker
    for mocked_sessionmaker in pytestconfig._mocked_sessionmakers:
        mocker.patch(mocked_sessionmaker, return_value=session)

    return session


@pytest.fixture(scope="function")
def db_session(_session, _transaction) -> Session:
    """
    Make sure all the different ways that we access the database in the code
    are scoped to a transactional context, and return a Session object that
    can interact with the database in the tests.

    Use this fixture in tests when you would like to use the SQLAlchemy ORM
    API, just as you might use a SQLAlchemy Session object.
    """
    return _session
