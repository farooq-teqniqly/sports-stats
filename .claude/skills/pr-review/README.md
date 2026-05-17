# pr-review

Comprehensive PR review skill. Produces a Markdown review file under `docs/` with severity-tagged findings, file:line citations, architecture notes, checklist, and questions for the author.

## What it does

1. Fetches existing PR comments (inline + issue-level) via `gh api` — Copilot, Qodo, humans — and builds a deduplicated index so it never re-raises issues already flagged.
2. Analyzes the current diff (staged/unstaged) or a specified PR.
3. Runs the review checklist: Functionality, Thread Safety, Performance, Code Quality, Simplification & Refactoring, Testing.
4. Writes the full review to `docs/PR_REVIEW*.md` and replies with the path.

## How to invoke

### Slash command
```
/pr-review
```

### With explicit context
```
/pr-review

**PR Context:**
- Feature/Change: <short description>
- PR Number/Link: #123
- Related Documentation: docs/<proposal>.md, docs/<review-guide>.md

**Review Scope:**
- Files Changed: <file list>
- Focus Areas: thread safety, error handling, event lifecycle
```

### Focused review
```
/pr-review

Review PR changes with focus on:
- Thread safety
- Error handling
- Test coverage
```

### Natural language
- "Review my PR"
- "Review the diff before I merge"
- "Run a code review on this branch"

## Prerequisites

- `gh` CLI authenticated (`gh auth status`) — required for fetching existing PR comments.
- Git repository with changes to review (staged, unstaged, or pushed PR).
- Optional: `docs/` dir with project-specific PR review guide (e.g. `docs/DYNAMIC_REFRESH_PR_REVIEW_GUIDE.md`) — skill auto-references if present.

## Output

- **File**: `docs/PR_REVIEW.md`, `docs/PR_REVIEW_<YYYY-MM-DD>.md`, or `docs/PR_REVIEW_pr-<number>.md`.
- **Document order**:
  1. Header (title, branch, scope metadata, `Reviewed commit: <short-hash>` line)
  2. Changelog (re-runs only; prior reviewed commits)
  3. Summary of findings (severity table)
  4. Existing review comments (dedup index table)
  5. TL;DR
  6. Architecture / data flow
  7. File-by-file notes
  8. Checklist
  9. Questions for author
  10. References
- **Findings tag**: `[New]` or `[Already raised by: {reviewer}]`.
- **Code refs**: every finding cites `path/to/file.ext:line` (or `:start-end`).

## Severity levels

| Severity | Use when |
|----------|----------|
| Critical | Bug, security flaw, data loss risk |
| High | Likely bug, broken contract, race condition |
| Medium | Wrong pattern, missing error handling, masked inconsistency |
| Low | Nice-to-have refactor, minor naming, small DRY win |
| Info | Future improvement, observation, non-blocking |

## Re-runs (incremental updates)

If review file already exists, skill reads `Reviewed commit:` from header, diffs `<old>..HEAD`, and updates the doc instead of overwriting:

- Header `Reviewed commit:` bumped to new HEAD; prior commit appended to **Changelog** section.
- Findings addressed by changes since old hash get marked `[Resolved in <short-hash>]` (kept for traceability).
- New findings raised only for changed code or newly-surfaced issues.
- Dedup index + severity table refreshed.
- Reply summarizes: `<old-short> → <new-short>` with resolved/new/outstanding counts.

## Tips

- Run after pushing PR so `gh api` can fetch existing comments — otherwise dedup step is skipped.
- If reviewing local diff (no PR yet), tell the skill: "no PR open yet, review staged changes".
- Point at relevant design docs or PR review guides in the prompt — skill follows their structure.
- For rename-heavy reviews, mention it explicitly so the skill cross-checks XML docs / tests / call sites for drift.

## Files

- `SKILL.md` — full skill instructions (loaded by Claude when triggered).
- `README.md` — this file.
