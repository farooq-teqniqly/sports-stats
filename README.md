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
utils/
  download_utils.py   # HTTP download + HTML save
  stats_utils.py      # Parse stats from saved HTML
tests/                # pytest files mirroring utils/
data/                 # Downloaded HTML, organized by sport/category
```

## Usage

**Download a page:**

```python
from utils.download_utils import download_url, save_html

response = download_url("https://www.basketball-reference.com/draft/NBA_2000.html")
save_html(response, "data/bball/drafts/nba_draft_2000.html")
```

**Parse stats from saved HTML:**

```python
from utils.stats_utils import get_draft_stats

for player in get_draft_stats("data/bball/drafts/nba_draft_2000.html", ["pts", "trb", "ast"]):
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
