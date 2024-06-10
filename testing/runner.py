"""Ruuner of tests in django project."""
from types import MethodType
from typing import Any

from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.test.runner import DiscoverRunner


def prepare_db(self):
    """Prepare the database by creating a schema if it does not exist.

    Args:
        self: database to connect
    """
    self.connect()
    self.connection.cursor().execute('CREATE SCHEMA IF NOT EXISTS competition_schema')


class PostgresSchemaRunner(DiscoverRunner):
    """Custom test runner for creating a schema in PostgreSQL database."""

    def setup_databases(self, **kwargs: Any) -> list[tuple[BaseDatabaseWrapper, str, bool]]:
        """
        Set up the databases by preparing the database connection.

        Args:
            kwargs: Additional keyword arguments.

        Returns:
            List of tuples containing database wrapper, alias, and autocreate flag.
        """
        for conn_name in connections:
            connection = connections[conn_name]
            connection.prepare_database = MethodType(prepare_db, connection)
        return super().setup_databases(**kwargs)
