# sports-stats

Scrapes and parses sports statistics from [Basketball Reference](https://www.basketball-reference.com).

## Setup

Requires Python 3.13+.

```powershell
# Create venv at project root
python -m venv .

# Install dev dependencies
.\Scripts\python.exe -m pip install -r requirements-dev.txt

# Install pre-commit hooks (runs Black on commit)
.\Scripts\python.exe -m pre_commit install
```

## Running Tests

```powershell
.\Scripts\python.exe -m pytest tests\ -v
```

## Project Layout

```
apps/
  import_nba_draft.py    # CLI: download + persist NBA draft advanced stats
utils/
  download_utils.py      # HTTP download + HTML save
  stats_utils.py         # Parse stats from saved HTML
  nba_draft_service.py   # Download + persist NBA draft advanced stats
models/
  __init__.py            # SQLAlchemy ORM models
migrations/              # Alembic migration scripts
tests/                   # pytest files mirroring utils/
data/                    # Downloaded HTML, organized by sport/category
```

## Usage

**Import NBA draft advanced stats into the database:**

```powershell
$env:SA_PASSWORD = "<password>"
.\scripts\python.exe apps\import_nba_draft.py 2000
```

Downloads the draft page to `data/bball/drafts/nba_draft_{year}.html`, upserts
players and advanced stats (`ws`, `ws_per_48`, `bpm`, `vorp`), and logs a warning
for any player row with missing stat values. `DB_NAME` defaults to `sports_stats`.

**Parse stats from saved HTML (low-level):**

```python
from utils.stats_utils import get_draft_stats

for player in get_draft_stats("data/bball/drafts/nba_draft_2000.html", ["ws", "bpm"]):
    print(player)
```

## Database Migrations

Migrations use [Alembic](https://alembic.sqlalchemy.org/) against SQL Server. Copy `.env.example` to `.env` and set credentials before running any migration command.

**Start SQL Server:**

```powershell
# Use podman if docker is not available
docker compose up -d
# or
podman compose up -d
```

**Create the database (first time only):**

```powershell
.\Scripts\python.exe -c "
import pyodbc, os
conn = pyodbc.connect(
    f'DRIVER={ODBC Driver 18 for SQL Server};SERVER=127.0.0.1,1433;DATABASE=master;UID=sa;PWD={os.environ[\"SA_PASSWORD\"]};TrustServerCertificate=yes',
    autocommit=True
)
conn.execute(\"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'sports_stats') CREATE DATABASE sports_stats\")
conn.close()
"
```

**Generate a migration after changing models:**

```powershell
$env:SA_PASSWORD = "<password>"; $env:DB_NAME = "sports_stats"
.\scripts\alembic.exe revision --autogenerate -m "describe your change"
```

Review the generated file in `migrations/versions/` before applying — autogenerate can miss some changes (e.g. renamed columns are detected as drop + add).

**Apply all pending migrations:**

```powershell
$env:SA_PASSWORD = "<password>"; $env:DB_NAME = "sports_stats"
.\scripts\alembic.exe upgrade head
```

**Other useful commands:**

```powershell
.\scripts\alembic.exe current          # show current revision
.\scripts\alembic.exe history          # list all revisions
.\scripts\alembic.exe downgrade -1     # roll back one revision
```

## Formatting

Black enforced via pre-commit. Run manually:

```powershell
black utils\ tests\
```
