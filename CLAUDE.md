# Conventions & Standards

## Project Layout

- `utils/` — shared utility modules
- `tests/` — pytest test files, mirroring `utils/` module names (`test_<module>.py`)
- `data/` — downloaded HTML files, organized by sport and category

## Python

- Python 3.13+
- Type annotations required on all function signatures
- Use `collections.abc.Generator` for generator return types
- No comments unless the why is non-obvious
- All public functions must have a docstring following PEP 257 (one-line or multi-line)

## Dependencies

- Runtime deps: `requirements.txt`
- Dev/test deps: `requirements-dev.txt` (uses `-r requirements.txt`)
- Pin exact versions in both files

## Coding Standards

- Validate all inputs at function boundaries; raise `ValueError` for bad args
- Call `response.raise_for_status()` before processing any HTTP response
- Use generators (`yield`) for functions that return collections of data
- Create parent directories with `Path.mkdir(parents=True, exist_ok=True)` before writing files
- Imports: stdlib → third-party → local, each group separated by a blank line

## Docker

- Use `docker` commands by default; if `docker` is not available, use `podman` instead

## Formatting

- Formatter: Black (enforced via pre-commit hook)
- Run `black utils\ tests\` manually if needed

## Git

- Commit subject line must be under 100 characters
- PR description must be under 100 words

## Testing

- Framework: pytest
- One test file per utility module (`tests/test_<module>.py`)
- Type annotations required on all fixtures and test functions (`-> None`, `-> Generator[T, None, None]`)
- Mock HTTP responses with `unittest.mock.MagicMock(spec=requests.Response)`
- Use `tmp_path` fixture for file I/O tests; always patch `_<DIR>` constants to `tmp_path` so tests never touch real data files
- Integration tests use testcontainers (`SqlServerContainer`) with explicit port binding and `127.0.0.1` (not `localhost`)
- Unit tests cover only what integration tests cannot: untriggerable branches (e.g. `player_id=None`), logging behavior, exact URL/value construction
- Do not duplicate in unit tests what is already verified end-to-end by integration tests
- Run `.\scripts\python.exe -m pytest tests\ -v` after **every code change**, before every commit — no exceptions, no ignores
- All tests (unit + integration) must pass locally before any commit or push; never rely on CI to catch failures
