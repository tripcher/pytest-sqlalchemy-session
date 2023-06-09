from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from pytest_sqlalchemy_session_test.app import db
from pytest_sqlalchemy_session_test.app.tables import sample_table


def create_instance_with_commit(instance_id: int) -> None:
    with db.session_factory() as session:
        session.execute(sample_table.insert(), {"id": instance_id})
        session.commit()


def insert_on_conflict_do_nothing(instance_id: int) -> None:
    with db.session_factory() as session, session.begin():
        stmt = insert(sample_table).values(id=instance_id).returning(sample_table)

        cursor = session.execute(stmt.on_conflict_do_nothing(index_elements=["id"]))
        cursor.first()


def create_instance_with_rollback(
    instance_id_before: int, instance_id_for_rollback: int, instance_id_after: int
) -> None:
    with db.session_factory() as session:
        session.execute(sample_table.insert(), {"id": instance_id_before})
        session.commit()
        session.execute(sample_table.insert(), {"id": instance_id_for_rollback})
        session.rollback()
        session.execute(sample_table.insert(), {"id": instance_id_after})
        session.commit()


def create_instance_with_begin(instance_id: int) -> None:
    with db.session_factory() as session, session.begin():
        session.execute(sample_table.insert(), {"id": instance_id})


def create_instance_with_multiple_begin_select_commit(instance_id: int) -> None:
    with db.session_factory() as session:
        with session.begin():
            session.execute(
                sample_table.select().where(sample_table.c.id == 1)
            ).fetchone()

        with session.begin():
            session.execute(sample_table.insert(), {"id": instance_id})


def create_commit_after_begin(instance_id: int) -> None:
    with db.session_factory() as session:
        with session.begin():
            session.execute(sample_table.insert(), {"id": instance_id})

        session.commit()


def execute_close_begin_commit(instance_id: int) -> None:
    with db.session_factory():
        pass

    with db.session_factory() as session:
        with session.begin():
            session.execute(sample_table.insert(), {"id": instance_id})

        session.commit()


def create_rollback_after_begin(instance_id: int) -> None:
    with db.session_factory() as session:
        with session.begin():
            session.execute(sample_table.insert(), {"id": instance_id})

        session.rollback()


def create_commit_after_insert_on_conflict_do_nothing_in_begin(
    instance_id: int,
) -> None:
    with db.session_factory() as session:
        with session.begin():
            stmt = insert(sample_table).values(id=instance_id).returning(sample_table)

            cursor = session.execute(stmt.on_conflict_do_nothing(index_elements=["id"]))
            cursor.first()

        session.commit()


def create_instance_with_multiple_begin_two_commits(
    instance_id: int, instance_id_2: int
) -> None:
    with db.session_factory() as session:
        with session.begin():
            session.execute(sample_table.insert(), {"id": instance_id})

        with session.begin():
            session.execute(sample_table.insert(), {"id": instance_id_2})


def create_instance_with_begin_nested(
    instance_id: int, nested_instance_id: int
) -> None:
    with db.session_factory() as session, session.begin():
        session.execute(sample_table.insert(), {"id": instance_id})

        with session.begin_nested():
            session.execute(sample_table.insert(), {"id": nested_instance_id})


def create_instance_with_rollback_begin_nested(
    instance_id: int,
    committed_nested_instance_id: int,
    rollback_nested_instance_id: int,
    committed_nested_instance_id_2: int,
) -> None:
    with db.session_factory() as session:
        session.begin()
        session.execute(sample_table.insert(), {"id": instance_id})

        session.begin_nested()
        session.execute(sample_table.insert(), {"id": committed_nested_instance_id})
        session.commit()

        session.begin_nested()
        session.execute(sample_table.insert(), {"id": rollback_nested_instance_id})
        session.rollback()

        session.begin_nested()
        session.execute(sample_table.insert(), {"id": committed_nested_instance_id_2})
        session.commit()

        session.commit()


def create_instance_with_commit_injection(session: Session, instance_id: int) -> None:
    session.execute(sample_table.insert(), {"id": instance_id})
    session.commit()


def create_instance_with_rollback_injection(
    session: Session,
    instance_id_before: int,
    instance_id_for_rollback: int,
    instance_id_after: int,
) -> None:
    session.execute(sample_table.insert(), {"id": instance_id_before})
    session.commit()
    session.execute(sample_table.insert(), {"id": instance_id_for_rollback})
    session.rollback()
    session.execute(sample_table.insert(), {"id": instance_id_after})
    session.commit()


def create_instance_with_begin_injection(session: Session, instance_id: int) -> None:
    with session.begin():
        session.execute(sample_table.insert(), {"id": instance_id})


def create_instance_with_begin_nested_injection(
    session: Session, instance_id: int, nested_instance_id
) -> None:
    with session.begin():
        session.execute(sample_table.insert(), {"id": instance_id})

    with session.begin_nested():
        session.execute(sample_table.insert(), {"id": nested_instance_id})
