import os

import pytest
from packaging import version

if version.parse(pytest.__version__).major < version.parse("7.0.0").major:
    from _pytest.pytester import Testdir
else:
    from pytest import Testdir  # type: ignore


pytest_plugins = "pytester"


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def conftest() -> str:
    """
    Load configuration file for the tests to a string, in order to run it in
    its own temporary directory.
    """
    with open(os.path.join(TEST_DIR, "_conftest.py"), "r") as conf:
        conftest = conf.read()

    return conftest


@pytest.fixture
def db_testdir(conftest, testdir: Testdir) -> Testdir:
    """
    Set up a temporary test directory loaded with the configuration file for
    the tests.
    """
    testdir.makeconftest(conftest)

    return testdir


@pytest.fixture
def db_testdir_with_mocked_sessionmaker(db_testdir: Testdir) -> Testdir:
    db_testdir.makeini(
        """
        [pytest]
        mocked-sessionmakers=pytest_sqlalchemy_session_test.app.db.session_factory
        """
    )

    return db_testdir
