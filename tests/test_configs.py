import logging

from conftest import Testdir  # type: ignore

logger = logging.getLogger(__name__)


def test_mocked_sessions(db_testdir: Testdir) -> None:
    """
    Test that we can specify paths to specific Session objects that the plugin
    will mock.
    """
    db_testdir.makeini(
        """
        [pytest]
        mocked-sessions=collections.namedtuple collections.Counter
    """
    )

    db_testdir.makepyfile(
        """
        def test_mocked_sessions(db_session):
            from collections import namedtuple, Counter
            assert str(namedtuple).startswith("<sqlalchemy.orm.session.TestSession")
            assert str(Counter).startswith("<sqlalchemy.orm.session.TestSession")
    """
    )

    result = db_testdir.runpytest("-v")

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=1)


def test_mocked_sessionmakers(db_testdir: Testdir) -> None:
    """
    Test that we can specify paths to specific Sessionmaker objects that the plugin
    will mock.
    """
    db_testdir.makeini(
        """
        [pytest]
        mocked-sessionmakers=collections.namedtuple collections.Counter
    """
    )

    db_testdir.makepyfile(
        """
        def test_mocked_sessionmakers(db_session):
            from collections import namedtuple, Counter

            assert str(namedtuple()).startswith("<sqlalchemy.orm.session.TestSession")
            assert str(Counter()).startswith("<sqlalchemy.orm.session.TestSession")
    """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=1)


def test_missing_db_fixture(testdir: Testdir) -> None:
    """
    Test that in the case where the user neglects to define a _db fixture, any
    tests requiring transactional context will raise an error.
    """
    # Create a conftest file that is missing a _db fixture but is otherwise
    # valid for a Flask-SQLAlchemy test suite
    conftest = """
        import pytest

        pytest_plugins = ['pytest_sqlalchemy_session.plugin']

    """

    testdir.makeconftest(conftest)

    # Define a test that will always pass, assuming that fixture setup works
    testdir.makepyfile(
        """
        def test_missing_db_fixture(db_session):
            assert True
    """
    )

    result = testdir.runpytest()
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*NotImplementedError: _db fixture not defined*"])
