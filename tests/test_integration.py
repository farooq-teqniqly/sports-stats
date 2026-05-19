import socket
import sys
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import Session
import warnings

from testcontainers.core.wait_strategies import ExecWaitStrategy

with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    from testcontainers.mssql import SqlServerContainer as _SqlServerContainer


class SqlServerContainer(_SqlServerContainer):
    """SqlServerContainer using structured wait strategy instead of deprecated decorator."""

    def _connect(self) -> None:
        ExecWaitStrategy(
            [
                "bash",
                "-c",
                '/opt/mssql-tools*/bin/sqlcmd -U "$SQLSERVER_USER" -P "$SA_PASSWORD" -Q \'SELECT 1\' -C',
            ]
        ).wait_until_ready(self)


sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import NBACareerStats, Player
from nba_draft_service import import_draft_class

_MSSQL_IMAGE = "mcr.microsoft.com/mssql/server:2025-latest"
_SA_PASSWORD = "IntegrationTest1!"
_DB_NAME = "sports_stats_test"
_DRAFT_YEAR = 2000
_PROJECT_ROOT = Path(__file__).parent.parent


def _free_port() -> int:
    """Return an available TCP port on the local machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def engine() -> Generator[Engine, None, None]:
    """Start SQL Server container, create DB, run migrations, yield engine."""
    # Podman on WSL2 only forwards explicitly-bound ports to the Windows host.
    # We pre-select a free port and bind it so Windows can reach the container.
    host_port = _free_port()
    container = SqlServerContainer(image=_MSSQL_IMAGE, password=_SA_PASSWORD)
    container.with_bind_ports(1433, host_port)

    with container:
        # Use 127.0.0.1 — on Windows, 'localhost' resolves to ::1 (IPv6) first,
        # but Podman containers only bind IPv4 (0.0.0.0).
        host = "127.0.0.1"

        master_url = URL.create(
            drivername="mssql+pyodbc",
            username="sa",
            password=_SA_PASSWORD,
            host=host,
            port=host_port,
            database="master",
            query={
                "driver": "ODBC Driver 18 for SQL Server",
                "TrustServerCertificate": "yes",
            },
        )
        master_engine = create_engine(master_url)
        with master_engine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            conn.execute(text(f"CREATE DATABASE {_DB_NAME}"))
        master_engine.dispose()

        db_url = URL.create(
            drivername="mssql+pyodbc",
            username="sa",
            password=_SA_PASSWORD,
            host=host,
            port=host_port,
            database=_DB_NAME,
            query={
                "driver": "ODBC Driver 18 for SQL Server",
                "TrustServerCertificate": "yes",
            },
        )

        alembic_cfg = Config(str(_PROJECT_ROOT / "alembic.ini"))
        # configparser treats % as interpolation; %% is the literal escape.
        url_for_alembic = db_url.render_as_string(hide_password=False).replace(
            "%", "%%"
        )
        alembic_cfg.set_main_option("sqlalchemy.url", url_for_alembic)
        upgrade(alembic_cfg, "head")

        db_engine = create_engine(db_url)
        yield db_engine
        db_engine.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Generator[Session, None, None]:
    """Open a session for one test, close after."""
    session = Session(engine)
    yield session
    session.close()


@pytest.fixture(autouse=True)
def clean_tables(db_session: Session) -> Generator[None, None, None]:
    """Delete all rows after each test (FK order: career_stats → players)."""
    yield
    db_session.execute(text("DELETE FROM nba.career_stats"))
    db_session.execute(text("DELETE FROM nba.players"))
    db_session.commit()


def test_players_persisted(db_session: Session) -> None:
    """Players are inserted and queryable after import."""
    import_draft_class(_DRAFT_YEAR, db_session)
    count = db_session.execute(select(func.count(Player.id))).scalar()
    assert count > 0
    player = db_session.get(Player, "martike01")
    assert player is not None
    assert player.name == "Kenyon Martin"
    assert player.draft_year == _DRAFT_YEAR
    assert player.draft_position == 1


def test_career_stats_persisted(db_session: Session) -> None:
    """Career stats for martike01 match expected values from cached HTML."""
    import_draft_class(_DRAFT_YEAR, db_session)
    stats = db_session.get(NBACareerStats, "martike01")
    assert stats is not None
    assert stats.ws == pytest.approx(48.0)
    assert stats.ws_48 == pytest.approx(0.1)
    assert stats.bpm == pytest.approx(0.1)
    assert stats.vorp == pytest.approx(12.1)


def test_import_idempotent(db_session: Session) -> None:
    """Calling import_draft_class twice produces no duplicate rows."""
    import_draft_class(_DRAFT_YEAR, db_session)
    count_1 = db_session.execute(select(func.count(Player.id))).scalar()

    import_draft_class(_DRAFT_YEAR, db_session)
    count_2 = db_session.execute(select(func.count(Player.id))).scalar()
    assert count_1 == count_2

    stats = db_session.get(NBACareerStats, "martike01")
    assert stats.ws == pytest.approx(48.0)
    assert stats.ws_48 == pytest.approx(0.1)
    assert stats.bpm == pytest.approx(0.1)
    assert stats.vorp == pytest.approx(12.1)


def test_year_validation(db_session: Session) -> None:
    """Year < 1947 raises ValueError before any DB interaction."""
    with pytest.raises(ValueError):
        import_draft_class(1946, db_session)


@patch("nba_draft_service.download_url")
def test_uses_cached_html(mock_download_url: MagicMock, db_session: Session) -> None:
    """download_url not called when HTML file is already cached on disk."""
    import_draft_class(_DRAFT_YEAR, db_session)
    mock_download_url.assert_not_called()


@patch.object(Path, "exists", return_value=False)
@patch("nba_draft_service.save_html")
@patch("nba_draft_service.download_url", side_effect=requests.HTTPError)
def test_http_error_propagates(
    mock_download_url: MagicMock, mock_save_html: MagicMock, mock_exists: MagicMock
) -> None:
    """HTTPError from download_url propagates out of import_draft_class."""
    with pytest.raises(requests.HTTPError):
        import_draft_class(_DRAFT_YEAR, MagicMock())
