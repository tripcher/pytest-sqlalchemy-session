import logging

from conftest import Testdir  # type: ignore

logger = logging.getLogger(__name__)


def test__usage_fixture__transaction_commit(db_testdir: Testdir) -> None:
    db_testdir.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        def test_transaction_commit(db_session):
            db_session.execute(sample_table.insert(), {"id": 1})
            db_session.commit()
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        def test_transaction_commit_changes_dont_persist(db_session):
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__usage_fixture__transaction_rollback(db_testdir: Testdir) -> None:
    db_testdir.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        def test_transaction_rollback(db_session):
            db_session.execute(sample_table.insert(), {"id": 1})
            db_session.commit()
            db_session.execute(sample_table.insert(), {"id": 2})
            db_session.rollback()
            db_session.execute(sample_table.insert(), {"id": 3})
            db_session.commit()

            instance_1 = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            instance_2 = db_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()
            instance_3 = db_session.execute(sample_table.select().where(sample_table.c.id == 3)).fetchone()

            assert instance_1 == (1,)
            assert instance_2 is None
            assert instance_3 == (3,)

        def test_transaction_rollback_changes_dont_persist(db_session):
            instance_1 = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            instance_2 = db_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()
            instance_3 = db_session.execute(sample_table.select().where(sample_table.c.id == 3)).fetchone()

            assert instance_1 is None
            assert instance_2 is None
            assert instance_3 is None
        """
    )

    result = db_testdir.runpytest()
    result.assert_outcomes(passed=2)


def test__usage_fixture__transaction_begin(db_testdir: Testdir) -> None:
    db_testdir.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        def test_transaction_begin(db_session):
            with db_session.begin():
                db_session.execute(sample_table.insert(), {"id": 1})

            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        def test_transaction_begin_changes_dont_persist(db_session):
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__usage_fixture__transaction_begin_nested(db_testdir: Testdir) -> None:
    db_testdir.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        def test_transaction_begin_nested(db_session):
            with db_session.begin():
                db_session.execute(sample_table.insert(), {"id": 1})

                with db_session.begin_nested():
                    db_session.execute(sample_table.insert(), {"id": 2})

            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            nested_instance = db_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance == (1,)
            assert nested_instance == (2,)

        def test_transaction_begin_nested_changes_dont_persist(db_session):
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            nested_instance = db_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance is None
            assert nested_instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__usage_fixture__transaction_begin_error(db_testdir: Testdir) -> None:
    db_testdir.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table

        def test_transaction_begin(db_session):
            with db_session.begin():
                db_session.execute(sample_table.insert(), {"id": 1})

                with db_session.begin():
                    db_session.execute(sample_table.insert(), {"id": 2})

        def test_transaction_begin_changes_dont_persist(db_session):
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(
        [
            "*FAILED test__usage_fixture__transaction_begin_error.py::test_transaction_begin*"
        ]
    )
    result.stdout.fnmatch_lines(
        [
            "*sqlalchemy.exc.InvalidRequestError: A transaction is already begun on this Session*"
        ]
    )


def test__code__transaction_commit(
    db_testdir_with_mocked_sessionmaker: Testdir,
) -> None:
    db_testdir_with_mocked_sessionmaker.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app.functions import create_instance_with_commit

        def test_transaction_commit(db_session):
            create_instance_with_commit(1)
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        def test_transaction_commit_changes_dont_persist(db_session):
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir_with_mocked_sessionmaker.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__code__transaction_rollback(
    db_testdir_with_mocked_sessionmaker: Testdir,
) -> None:
    db_testdir_with_mocked_sessionmaker.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app.functions import create_instance_with_rollback

        def test_transaction_rollback(db_session):
            create_instance_with_rollback(
                instance_id_before=1,
                instance_id_for_rollback=2,
                instance_id_after=3
            )

            instance_1 = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            instance_2 = db_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()
            instance_3 = db_session.execute(sample_table.select().where(sample_table.c.id == 3)).fetchone()

            assert instance_1 == (1,)
            assert instance_2 is None
            assert instance_3 == (3,)

        def test_transaction_rollback_changes_dont_persist(db_session):
            instance_1 = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            instance_2 = db_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()
            instance_3 = db_session.execute(sample_table.select().where(sample_table.c.id == 3)).fetchone()

            assert instance_1 is None
            assert instance_2 is None
            assert instance_3 is None
        """
    )

    result = db_testdir_with_mocked_sessionmaker.runpytest()
    result.assert_outcomes(passed=2)


def test__code__transaction_begin(db_testdir_with_mocked_sessionmaker: Testdir) -> None:
    db_testdir_with_mocked_sessionmaker.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app.functions import create_instance_with_begin

        def test_transaction_begin(db_session):
            create_instance_with_begin(1)

            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance == (1,)

        def test_transaction_begin_changes_dont_persist(db_session):
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir_with_mocked_sessionmaker.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__code__transaction_begin_nested(
    db_testdir_with_mocked_sessionmaker: Testdir,
) -> None:
    db_testdir_with_mocked_sessionmaker.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app.functions import create_instance_with_begin_nested

        def test_transaction_begin_nested(db_session):
            create_instance_with_begin_nested(1, 2)

            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            nested_instance = db_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance == (1,)
            assert nested_instance == (2,)

        def test_transaction_begin_nested_changes_dont_persist(db_session):
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()
            nested_instance = db_session.execute(sample_table.select().where(sample_table.c.id == 2)).fetchone()

            assert instance is None
            assert nested_instance is None
        """
    )

    result = db_testdir_with_mocked_sessionmaker.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=2)


def test__code__transaction_begin_error(
    db_testdir_with_mocked_sessionmaker: Testdir,
) -> None:
    db_testdir_with_mocked_sessionmaker.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app.functions import create_instance_with_begin

        def test_transaction_begin(db_session):
            with db_session.begin():
                db_session.execute(sample_table.insert(), {"id": 1})

                create_instance_with_begin(2)

        def test_transaction_begin_changes_dont_persist(db_session):
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir_with_mocked_sessionmaker.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(
        ["*FAILED test__code__transaction_begin_error.py::test_transaction_begin*"]
    )
    result.stdout.fnmatch_lines(
        [
            "*sqlalchemy.exc.InvalidRequestError: A transaction is already begun on this Session*"
        ]
    )


def test__sqlalchemy__begin_error(db_testdir: Testdir) -> None:
    """
    Check that original sqlalchemy.Session.begin raise InvalidRequestError.
    """
    db_testdir.makepyfile(
        """
        from pytest_sqlalchemy_session_test.app.tables import sample_table
        from pytest_sqlalchemy_session_test.app import db

        def test_transaction_commit(database):
            with db.session_factory() as session, session.begin():
                session.execute(sample_table.insert(), {"id": 1})

                with session.begin():
                    session.execute(sample_table.insert(), {"id": 2})

        def test_transaction_commit_changes_dont_persist(db_session):
            instance = db_session.execute(sample_table.select().where(sample_table.c.id == 1)).fetchone()

            assert instance is None
        """
    )

    result = db_testdir.runpytest()

    logger.info(result.stdout.str())
    result.assert_outcomes(passed=1, failed=1)
    result.stdout.fnmatch_lines(
        ["*FAILED test__sqlalchemy__begin_error.py::test_transaction_commit*"]
    )
    result.stdout.fnmatch_lines(
        [
            "*sqlalchemy.exc.InvalidRequestError: A transaction is already begun on this Session*"
        ]
    )
