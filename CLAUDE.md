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

## Testing

- Framework: pytest
- One test file per utility module
- Mock HTTP responses with `unittest.mock.MagicMock(spec=requests.Response)`
- Use `tmp_path` fixture for file I/O tests
- Test both happy path and error/edge cases (empty input, unknown keys, failed responses)
- Run `.\scripts\python.exe -m pytest tests\ -v` after every code change; all tests must pass before a task is complete
