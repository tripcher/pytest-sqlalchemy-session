import os

import pytest
from pytest import Pytester

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
def db_testdir(conftest, pytester: Pytester) -> Pytester:
    """
    Set up a temporary test directory loaded with the configuration file for
    the tests.
    """
    pytester.makeconftest(conftest)

    return pytester


@pytest.fixture
def db_testdir_with_strict_mode(db_testdir: Pytester) -> Pytester:
    db_testdir.makeini(
        """
        [pytest]
        strict-db=True
        """
    )

    return db_testdir
