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

## Formatting

Black enforced via pre-commit. Run manually:

```powershell
black utils\ tests\
```
