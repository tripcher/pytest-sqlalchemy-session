import logging

from pytest import Pytester

logger = logging.getLogger(__name__)


def test__marker__transaction_commit(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
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

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__marker__transaction_commit_not_affect_another_test(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        @pytest.mark.sqlalchemy_db
        def test_transaction_commit(custom_session):
            custom_session.execute(sample_table.insert(), {"id": 1})
            custom_session.commit()
            instance_1 = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()


            assert instance_1 == (1,)

        def test_transaction_commit(custom_session):
            custom_session.execute(sample_table.insert(), {"id": 2})
            custom_session.commit()
            instance_2 = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance_2 == (2,)

        def test_transaction_commit_changes_dont_persist(custom_session):
            instance_1 = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            instance_2 = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance_1 is None
            assert instance_2 == (2,)
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__marker__transaction_commit_mix_markers(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        @pytest.mark.sqlalchemy_db
        def test_transaction_commit(custom_session):
            custom_session.execute(sample_table.insert(), {"id": 1})
            custom_session.commit()
            instance_1 = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()


            assert instance_1 == (1,)

        @pytest.mark.transactional_db
        def test_transaction_commit(custom_session):
            custom_session.execute(sample_table.insert(), {"id": 2})
            custom_session.commit()
            instance_2 = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance_2 == (2,)

        def test_transaction_commit_changes_dont_persist(custom_session):
            instance_1 = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            instance_2 = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance_1 is None
            assert instance_2 == (2,)
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__marker__transaction_rollback(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        @pytest.mark.sqlalchemy_db
        def test_transaction_rollback(custom_session):
            custom_session.execute(sample_table.insert(), {"id": 1})
            custom_session.commit()
            custom_session.execute(sample_table.insert(), {"id": 2})
            custom_session.rollback()
            custom_session.execute(sample_table.insert(), {"id": 3})
            custom_session.commit()

            instance_1 = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            instance_2 = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()
            instance_3 = custom_session.execute(sample_table.select().where(sample_table.c.id == 3)).fetchone()

            assert instance_1 == (1,)
            assert instance_2 is None
            assert instance_3 == (3,)

        @pytest.mark.sqlalchemy_db
        def test_transaction_rollback_changes_dont_persist(custom_session):
            instance_1 = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            instance_2 = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()
            instance_3 = custom_session.execute(sample_table.select().where(sample_table.c.id == 3)).fetchone()

            assert instance_1 is None
            assert instance_2 is None
            assert instance_3 is None
        """
    )

    result = db_testdir.runpytest()
    result.assert_outcomes(passed=2)


def test__marker__transaction_begin(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin(custom_session):
            with custom_session.begin():
                custom_session.execute(sample_table.insert(), {"id": 1})

            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin_changes_dont_persist(custom_session):
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__marker__transaction_begin_nested(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin_nested(custom_session):
            with custom_session.begin():
                custom_session.execute(sample_table.insert(), {"id": 1})

                with custom_session.begin_nested():
                    custom_session.execute(sample_table.insert(), {"id": 2})

            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            nested_instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance == (1,)
            assert nested_instance == (2,)

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin_nested_changes_dont_persist(custom_session):
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            nested_instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance is None
            assert nested_instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__marker__transaction_begin_error(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin(custom_session):
            with custom_session.begin():
                custom_session.execute(sample_table.insert(), {"id": 1})

                with custom_session.begin():
                    custom_session.execute(sample_table.insert(), {"id": 2})

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin_changes_dont_persist(custom_session):
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(
        ["*FAILED test__marker__transaction_begin_error.py::test_transaction_begin*"]
    )
    result.stdout.fnmatch_lines(
        [
            "*sqlalchemy.exc.InvalidRequestError: A transaction is already begun on this Session*"
        ]
    )


def test__marker__code_transaction_commit(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app.functions import create_instance_with_commit

        @pytest.mark.sqlalchemy_db
        def test_transaction_commit(custom_session):
            create_instance_with_commit(1)
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        @pytest.mark.sqlalchemy_db
        def test_transaction_commit_changes_dont_persist(custom_session):
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__marker__code_transaction_rollback(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app.functions import create_instance_with_rollback

        @pytest.mark.sqlalchemy_db
        def test_transaction_rollback(custom_session):
            create_instance_with_rollback(
                instance_id_before=1,
                instance_id_for_rollback=2,
                instance_id_after=3
            )

            instance_1 = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            instance_2 = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()
            instance_3 = custom_session.execute(sample_table.select().where(sample_table.c.id == 3)).fetchone()

            assert instance_1 == (1,)
            assert instance_2 is None
            assert instance_3 == (3,)

        def test_transaction_rollback_changes_dont_persist(custom_session):
            instance_1 = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            instance_2 = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()
            instance_3 = custom_session.execute(sample_table.select().where(sample_table.c.id == 3)).fetchone()

            assert instance_1 is None
            assert instance_2 is None
            assert instance_3 is None
        """
    )

    result = db_testdir.runpytest()
    result.assert_outcomes(passed=2)


def test__marker__code_transaction_begin(db_testdir: Pytester) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app.functions import create_instance_with_begin

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin(custom_session):
            create_instance_with_begin(1)

            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin_changes_dont_persist(custom_session):
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__marker__code_transaction_begin_nested(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app.functions import create_instance_with_begin_nested

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin_nested(custom_session):
            create_instance_with_begin_nested(1, 2)

            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            nested_instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance == (1,)
            assert nested_instance == (2,)

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin_nested_changes_dont_persist(custom_session):
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            nested_instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance is None
            assert nested_instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__marker__code_transaction_begin_error(
    db_testdir: Pytester,
) -> None:
    db_testdir.makepyfile(
        """
        import pytest
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app.functions import create_instance_with_begin

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin(custom_session):
            with custom_session.begin():
                custom_session.execute(sample_table.insert(), {"id": 1})

                create_instance_with_begin(2)

        @pytest.mark.sqlalchemy_db
        def test_transaction_begin_changes_dont_persist(custom_session):
            instance = custom_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(
        [
            "*FAILED test__marker__code_transaction_begin_error.py::test_transaction_begin*"
        ]
    )
    result.stdout.fnmatch_lines(
        [
            "*sqlalchemy.exc.InvalidRequestError: A transaction is already begun on this Session*"
        ]
    )
