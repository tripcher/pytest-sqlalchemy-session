import logging

from pytest import Pytester

logger = logging.getLogger(__name__)


def test_missing_db_fixture(pytester: Pytester) -> None:
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

    pytester.makeconftest(conftest)

    # Define a test that will always pass, assuming that fixture setup works
    pytester.makepyfile(
        """
        def test_missing_db_fixture(db_session):
            assert True
    """
    )

    result = pytester.runpytest()
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*NotImplementedError: _db fixture not defined*"])
