"""Explicit transaction ownership for multi-repository career operations."""

import sqlite3

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


class DatabaseBusy(Exception):
    """The write lock could not be obtained within the configured timeout."""


def _busy(error):
    return getattr(error.orig, "sqlite_errorcode", 0) & 0xFF in {
        sqlite3.SQLITE_BUSY,
        sqlite3.SQLITE_LOCKED,
    }


class WorkSession(Session):
    """Only the unit of work may finish the transaction."""

    def commit(self):
        raise RuntimeError("Unit of work owns the transaction")

    def rollback(self):
        raise RuntimeError("Unit of work owns the transaction")


class UnitOfWork:
    def __init__(self, engine):
        self._engine = engine
        self._connection = None
        self._session = None
        self._used = False

    def __enter__(self):
        if self._used:
            raise RuntimeError("Unit of work cannot be reused")
        self._used = True
        self._connection = self._engine.connect()
        try:
            self._connection.exec_driver_sql("BEGIN IMMEDIATE")
            self._session = WorkSession(
                bind=self._connection,
                join_transaction_mode="rollback_only",
                close_resets_only=False,
            )
        except OperationalError as error:
            self._connection.close()
            if _busy(error):
                raise DatabaseBusy("Database is temporarily unavailable") from None
            raise
        except BaseException:
            self._connection.close()
            raise
        return self

    @property
    def session(self):
        if self._session is None:
            raise RuntimeError("Unit of work is not active")
        return self._session

    def __exit__(self, exc_type, exc, traceback):
        connection, session = self._connection, self._session
        try:
            if exc_type is not None:
                connection.rollback()
            else:
                session.flush()
                if not connection.in_transaction():
                    raise RuntimeError("Unit of work transaction was ended prematurely")
                connection.commit()
        except OperationalError as error:
            connection.rollback()
            if _busy(error):
                raise DatabaseBusy("Database is temporarily unavailable") from None
            raise
        except BaseException:
            connection.rollback()
            raise
        finally:
            session.close()
            connection.close()
            self._session = None
            self._connection = None
        return False
