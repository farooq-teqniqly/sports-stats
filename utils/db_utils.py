"""Shared database connection utilities."""

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine


def build_connection_url(password: str, db_name: str) -> URL:
    """Build a SQLAlchemy URL for SQL Server via ODBC Driver 18.

    Args:
        password: SA account password. Must not be empty.
        db_name: Target database name. Must not be empty.

    Returns:
        A SQLAlchemy URL with the password safely percent-encoded.

    Raises:
        ValueError: If password or db_name is empty.
    """
    if not password:
        raise ValueError("password must not be empty")
    if not db_name:
        raise ValueError("db_name must not be empty")
    return URL.create(
        drivername="mssql+pyodbc",
        username="sa",
        password=password,
        host="127.0.0.1",
        port=1433,
        database=db_name,
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "TrustServerCertificate": "yes",
        },
    )


def build_engine(password: str, db_name: str) -> Engine:
    """Create a SQLAlchemy Engine for SQL Server.

    Args:
        password: SA account password. Must not be empty.
        db_name: Target database name. Must not be empty.

    Returns:
        A configured SQLAlchemy Engine.

    Raises:
        ValueError: If password or db_name is empty.
    """
    return create_engine(build_connection_url(password, db_name))
