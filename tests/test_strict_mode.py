import logging

from pytest import Pytester

logger = logging.getLogger(__name__)


def test__strict_mode__usage_only_fixture(
    db_testdir_with_strict_mode: Pytester,
) -> None:
    db_testdir_with_strict_mode.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        def test_transaction_commit(db_session):
            db_session.execute(sample_table.insert(), {"id": 1})
            db_session.commit()
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)
        """
    )

    result = db_testdir_with_strict_mode.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        ["*FAILED test__strict_mode__usage_only_fixture.py::test_transaction_commit*"]
    )
    result.stdout.fnmatch_lines(
        [
            "*_pytest.config.exceptions.UsageError: "
            "The pytest.mark.sqlalchemy_db or pytest.mark.transactional_db marker is required to execute db queries.*"
        ]
    )


def test__strict_mode__without_marker(db_testdir_with_strict_mode: Pytester) -> None:
    db_testdir_with_strict_mode.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        def test_transaction_commit(custom_session):
            custom_session.execute(sample_table.insert(), {"id": 1})
            custom_session.commit()
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)
        """
    )

    result = db_testdir_with_strict_mode.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        ["*FAILED test__strict_mode__without_marker.py::test_transaction_commit*"]
    )
    result.stdout.fnmatch_lines(
        [
            "*_pytest.config.exceptions.UsageError: "
            "The pytest.mark.sqlalchemy_db or pytest.mark.transactional_db marker is required to execute db queries.*"
        ]
    )


def test__strict_mode__marker_dont_affect_another_test(
    db_testdir_with_strict_mode: Pytester,
) -> None:
    db_testdir_with_strict_mode.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        @pytest.mark.sqlalchemy_db
        def test_transaction_commit__with_marker(custom_session):
            custom_session.execute(sample_table.insert(), {"id": 1})
            custom_session.commit()
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        def test_transaction_commit__without_marker(custom_session):
            custom_session.execute(sample_table.insert(), {"id": 1})
            custom_session.commit()
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)
        """
    )

    result = db_testdir_with_strict_mode.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(
        [
            "*FAILED test__strict_mode__marker_dont_affect_another_test.py::test_transaction_commit__without_marker*"
        ]
    )
    result.stdout.fnmatch_lines(
        [
            "*_pytest.config.exceptions.UsageError: "
            "The pytest.mark.sqlalchemy_db or pytest.mark.transactional_db marker is required to execute db queries.*"
        ]
    )


def test__strict_mode__usage_fixture_and_marker(
    db_testdir_with_strict_mode: Pytester,
) -> None:
    db_testdir_with_strict_mode.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        @pytest.mark.sqlalchemy_db
        def test_transaction_commit(db_session):
            db_session.execute(sample_table.insert(), {"id": 1})
            db_session.commit()
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        @pytest.mark.sqlalchemy_db
        def test_transaction_commit_changes_dont_persist(db_session):
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir_with_strict_mode.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__strict_mode__usage_marker(db_testdir_with_strict_mode: Pytester) -> None:
    db_testdir_with_strict_mode.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        @pytest.mark.sqlalchemy_db
        def test_transaction_commit(custom_session):
            custom_session.execute(sample_table.insert(), {"id": 1})
            custom_session.commit()
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        @pytest.mark.sqlalchemy_db
        def test_transaction_commit_changes_dont_persist(custom_session):
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir_with_strict_mode.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__strict_mode__usage_transactional_marker(
    db_testdir_with_strict_mode: Pytester,
) -> None:
    db_testdir_with_strict_mode.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        @pytest.mark.transactional_db
        def test_transaction_commit(custom_session):
            custom_session.execute(sample_table.insert(), {"id": 1})
            custom_session.commit()
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        @pytest.mark.transactional_db
        def test_transaction_commit_changes_dont_persist(custom_session):
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)
        """
    )

    result = db_testdir_with_strict_mode.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)
