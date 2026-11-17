"""A unit of work owns one immediate transaction and closes it permanently."""

import pytest
from resume_core.database import make_engine
from resume_core.persistence.unit_of_work import DatabaseBusy, UnitOfWork
from sqlalchemy import text
from sqlalchemy.exc import InvalidRequestError, ResourceClosedError


def setup_engine(tmp_path):
    engine = make_engine(tmp_path / "uow.sqlite3")
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE left_side (value TEXT)")
        connection.exec_driver_sql("CREATE TABLE right_side (value TEXT)")
    return engine


def test_shared_transaction_commits_both_and_closes_references(tmp_path):
    engine = setup_engine(tmp_path)
    work = UnitOfWork(engine)
    with work:
        session = work.session
        connection = session.connection()
        session.execute(text("INSERT INTO left_side VALUES ('one')"))
        session.execute(text("INSERT INTO right_side VALUES ('two')"))
    with engine.connect() as check:
        assert check.exec_driver_sql("SELECT value FROM left_side").scalar_one() == "one"
        assert check.exec_driver_sql("SELECT value FROM right_side").scalar_one() == "two"
    with pytest.raises(InvalidRequestError):
        session.execute(text("SELECT 1"))
    with pytest.raises(ResourceClosedError):
        connection.exec_driver_sql("SELECT 1")
    with pytest.raises(RuntimeError):
        _ = work.session
    with pytest.raises(RuntimeError):
        work.__enter__()


def test_exception_rolls_back_all_repositories(tmp_path):
    engine = setup_engine(tmp_path)
    with pytest.raises(ValueError):
        with UnitOfWork(engine) as work:
            work.session.execute(text("INSERT INTO left_side VALUES ('one')"))
            work.session.execute(text("INSERT INTO right_side VALUES ('two')"))
            raise ValueError("synthetic")
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT count(*) FROM left_side").scalar_one() == 0
        assert connection.exec_driver_sql("SELECT count(*) FROM right_side").scalar_one() == 0


def test_competing_writer_fails_safely_then_can_write(tmp_path):
    engine = setup_engine(tmp_path)
    with UnitOfWork(engine) as first:
        first.session.execute(text("INSERT INTO left_side VALUES ('one')"))
        with pytest.raises(DatabaseBusy, match="temporarily unavailable") as failure:
            with UnitOfWork(engine):
                pass
        assert "locked" not in str(failure.value)
    with UnitOfWork(engine) as second:
        second.session.execute(text("INSERT INTO right_side VALUES ('two')"))
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT count(*) FROM right_side").scalar_one() == 1


def test_session_cannot_end_owned_transaction(tmp_path):
    engine = setup_engine(tmp_path)
    with UnitOfWork(engine) as work:
        work.session.execute(text("INSERT INTO left_side VALUES ('one')"))
        with pytest.raises(RuntimeError, match="owns the transaction"):
            work.session.commit()
        with pytest.raises(RuntimeError, match="owns the transaction"):
            work.session.rollback()
        work.session.execute(text("INSERT INTO right_side VALUES ('two')"))
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT count(*) FROM left_side").scalar_one() == 1
        assert connection.exec_driver_sql("SELECT count(*) FROM right_side").scalar_one() == 1
