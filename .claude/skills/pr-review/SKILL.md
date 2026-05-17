---
name: pr-review
description: Perform a comprehensive PR review of the current workspace changes (or a specified PR), following a structured review guide. Fetches existing PR comments via `gh api` to deduplicate, then writes a full Markdown review under `docs/` with severity-tagged findings, file:line citations, architecture/data flow notes, checklist, and questions for the author. Use when the user invokes /pr-review, asks for a PR review, or wants code changes reviewed before merge.
---

# pr-review

Comprehensive PR review. Canonical artifact = Markdown file under `docs/`. Chat reply only summarizes/links.

## Format

- **Structure**: clear sections with headers; professional, actionable Markdown with code snippets and checkboxes.
- **Code references**: every finding includes **repo-relative path + line number(s)** (e.g. `src/Module/Foo.cs:42` or `:42-55`). Add symbol/method names when helpful. Never omit path+lines for workspace code.
- **Deliverable**: always write complete review to Markdown file on disk (see "Output file"). Chat reply summarizes/links.
- **Risks at top**: **Summary of findings** table (severity, tag, topic, location, **source**) appears immediately after header/metadata, before TL;DR/architecture/file-by-file. The **Source** column identifies who surfaced each finding: `Claude` (this skill), `Qodo`, `Copilot`, or `Human` (named reviewer). When multiple parties flagged the same issue, list all (e.g. `Qodo, Claude`).

## Output file

1. Create or overwrite Markdown under `docs/` (create dir if missing). Names:
   - `docs/PR_REVIEW.md`, or
   - `docs/PR_REVIEW_<YYYY-MM-DD>.md`, or
   - `docs/PR_REVIEW_pr-<number>.md` when PR number known
2. Entire review body in that file (all sections, findings, checklist, snippets).
3. **Header metadata must include `Reviewed commit:` line** with short commit hash (`git rev-parse --short HEAD`) and branch. Example:
   ```
   Reviewed commit: 9f4a2c1 on branch feature/foo
   ```
4. Mention exact path in reply.

## Incremental updates (re-runs)

Before fresh review, check whether output file already exists at chosen path:

1. If exists, parse `Reviewed commit:` from header.
2. Run `git diff <old-hash>..HEAD` (and `git log <old-hash>..HEAD --oneline`) to get changes since previous review.
3. **Update mode** — do not overwrite full document:
   - Update header `Reviewed commit:` to new short hash + branch.
   - Add **Changelog** section directly under header listing prior reviewed commits (append, do not replace) — format: `- <date> <short-hash> — <one-line summary of delta>`.
   - For each existing finding: if change since old hash addresses it, mark **[Resolved in <short-hash>]** with path:line of fix; keep entry for traceability.
   - Add new findings only for code changed in `<old-hash>..HEAD` diff or newly-surfaced issues.
   - Refresh dedup index from latest `gh api` comments (new comments may have arrived).
   - Refresh Summary of findings table to reflect resolved/new/outstanding state.
4. If existing file lacks `Reviewed commit:` (legacy), treat as fresh review and overwrite, but preserve any reviewer-author dialogue at bottom under **Prior notes** heading.

In reply, state: "Updated review from `<old-short>` → `<new-short>` (N resolved, M new, K outstanding)" + path.

## Review process

### 1. Gather existing review comments first

Before analyzing code, fetch all existing review comments via `gh` CLI to avoid duplicates:

```bash
# Inline review comments (Copilot, Qodo, humans)
gh api repos/{owner}/{repo}/pulls/{pr}/comments

# General (issue-level) PR comments
gh api repos/{owner}/{repo}/issues/{pr}/comments
```

For each comment note: **who** (human/Copilot/Qodo bot), **what** (one-line summary), **resolved?** (author replied/marked resolved).

Pay attention to **human inline rename requests** for methods/types/members. Treat as acceptance criteria: compare current symbol names in workspace, mark **resolved** vs **outstanding** with path:line. If code renamed but XML docs/tests/call sites still use old wording, flag as follow-up.

Build deduplicated index. When own finding matches existing comment: do not re-raise; note *"Already raised by [reviewer]"* with brief acknowledgement if significant.

### 2. Analysis steps

1. Follow structure from any relevant PR review guide (e.g. `docs/DYNAMIC_REFRESH_PR_REVIEW_GUIDE.md`):
   - Summary of findings (severity table) at top
   - TL;DR: what changed and why
   - Architecture/data flow if applicable
   - Key design decisions and trade-offs
   - High-risk areas first; cite path:line each
   - Checklist (Functionality, Thread Safety, Performance, Code Quality, Testing)

2. For each file/area:
   - What changed and why it matters
   - Issues (bugs, security, performance, maintainability)
   - Alignment with existing patterns/standards
   - **Naming vs review feedback**: verify human-requested renames implemented (or document why not). Check doc comments + names stay aligned (avoid generic method names with comments describing only old narrower behavior unless intentional).
   - **Simplification/refactoring**: duplicated sync/async logic, repeated catch/error-mapping, large methods, copy-pasted code extractable to helper. Flag **Low**/**Info** with concrete before/after sketches.
   - Test coverage; suggest gaps
   - Breaking changes / migration concerns

3. Provide:
   - Summary of findings at top — include **Source** column: `Claude`, `Qodo`, `Copilot`, or `Human` (named reviewer). If multiple parties caught the same issue, list all.
   - Locations as `path:startLine` (or range); add symbol/method in prose
   - Tag each finding **[New]** or **[Already raised by: {reviewer}]**
   - Recommendations + questions for author

4. Reference standards: `.cursor/rules/TDD_IMPLEMENTATION.cursorrules`, codebase patterns, error handling/logging, thread safety.

## Review checklist

### Functionality
- [ ] Core functionality works as intended
- [ ] Edge cases handled
- [ ] Error scenarios covered
- [ ] Configuration correct

### Thread safety
- [ ] Concurrent operations safe
- [ ] Synchronization appropriate
- [ ] No race conditions
- [ ] Disposal thread-safe

### Performance
- [ ] No unnecessary blocking
- [ ] Efficient algorithms/data structures
- [ ] Proper caching strategies
- [ ] Background ops don't impact request paths

### Code quality
- [ ] Follows existing patterns
- [ ] Proper error handling and logging
- [ ] Clear and maintainable
- [ ] Appropriate separation of concerns
- [ ] Human reviewer rename requests implemented (or deferred with rationale); docs/tests/call sites updated

### Simplification & refactoring
- [ ] No duplicated logic across sync/async or similar variants
- [ ] Repeated error-mapping/catch/boilerplate extracted to helpers
- [ ] Large methods decomposed into single-responsibility pieces
- [ ] No copy-pasted blocks consolidatable (DRY)

### Testing
- [ ] Adequate coverage
- [ ] Follows project patterns (xUnit/NUnit)
- [ ] Error cases tested
- [ ] Integration tests if applicable

## Specialized review modes

### Architecture
1. Understand data/control flow
2. Review key design decisions and trade-offs
3. Check separation of concerns
4. Verify integration points and dependencies
5. Assess scalability/performance implications
6. Provide architecture diagram or flow description if helpful

### Test coverage
1. Identify all code paths and edge cases
2. Tests cover: happy paths, errors, edges (null/empty/concurrent), integration
3. Verify quality: framework patterns (xUnit/NUnit), mocking (NSubstitute/Moq per project), clear names/structure
4. Suggest additional tests if gaps
5. Reference test coverage docs (e.g. `docs/DYNAMIC_REFRESH_TEST_COVERAGE.md`)

### Thread safety
1. Identify shared state and resources
2. Check synchronization: locks/granularity, ConcurrentDictionary, thread-safe collections, disposal patterns
3. Race conditions: check-then-act, event sub/unsubscribe, disposal vs ongoing ops
4. Verify proper disposal/cleanup
5. Cite synchronization points with path:line

### Simplification & refactoring
1. Duplicated logic introduced/exposed by PR: sync/async pairs with identical catch/finally, repeated error-to-result mapping, copy-pasted boilerplate (e.g. Commands/Queries controller bases)
2. Large methods doing too many things: split validation, mapping, orchestration, logging
3. Consolidation: switch expressions or dictionaries instead of long if/else or catch chains; shared base classes vs parallel implementations
4. Provide concrete sketch (pseudocode/snippet) of simplified form
5. Severity: **Low**/**Info**; raise to **Medium** if duplication actively causing bugs (e.g. new catch added in one copy but forgotten in other)

### Performance
1. Identify performance-sensitive paths
2. Check: blocking ops, inefficient algorithms/data structures, memory leaks/disposal, caching
3. Verify: background ops don't block request paths, efficient change detection (e.g. hashing), surgical updates
4. Note any performance numbers (measured vs estimated)
5. Reference PR review guide's "Performance Considerations" if available

## Guidelines

- Cite locations precisely with path:line(s) from current workspace.
- High-risk first: thread safety, error handling, performance hot paths.
- Be actionable: specific recommendations, not observations.
- Check existing patterns/conventions.
- Reference design docs, proposals, review guides.
- Ask questions if unclear.

## Execution flow

1. Capture HEAD short hash: `git rev-parse --short HEAD` and current branch — record for header `Reviewed commit:` line.
2. **Check if output file exists** at chosen path. If yes, parse prior `Reviewed commit:` and switch to **incremental update mode** (see "Incremental updates"): diff `<old>..HEAD`, scope analysis to changed code, mark prior findings resolved where addressed, append Changelog entry.
3. Fetch all existing PR comments (inline + issue-level) via `gh api`
4. Build deduplicated index before writing findings
5. For each human-requested rename, verify current code + related docs/tests; mark resolved/open with path:line
6. Analyze current git changes (staged/unstaged) — on re-run, scope to `<old-hash>..HEAD` diff
7. Identify problem and solution approach
8. Review architecture/data flow if applicable
9. Examine key design decisions and trade-offs
10. High-risk areas first; cite path:line
11. Run checklist (Functionality, Thread Safety, Performance, Code Quality, Testing)
12. Per file/area: explain change, identify issues, check patterns, find simplification opportunities, verify test coverage
13. Write full review to `docs/` Markdown. **Document order:**
    1. Header (title, branch, scope metadata, **`Reviewed commit: <short-hash>` line**)
    2. Changelog (only present on re-runs; lists prior reviewed commits)
    3. Summary of findings (severity table; mark resolved/new/outstanding on re-runs)
    4. Existing review comments (deduplicated index table)
    5. TL;DR
    6. Architecture/data flow
    7. File-by-file notes
    8. Checklist
    9. Questions for author
    10. References
14. Reply with path to saved file and optional highlights. On re-run, include resolved/new/outstanding counts and old→new short-hash.

## When to use

- `/pr-review` slash command
- User asks for PR review
- Reviewing changes before merge / validating against standards

## Example usage

```
/pr-review
```

With context:
```
/pr-review

**PR Context:**
- Feature/Change: Dynamic External Identity Provider Refresh
- PR Number/Link: #123
- Related Documentation: docs/EXTERNAL_AUTHENTICATOR_REFRESH_PROPOSAL_v7.md, docs/DYNAMIC_REFRESH_PR_REVIEW_GUIDE.md

**Review Scope:**
- Files Changed: ExternalIdPStore.cs, MiddlewareCacheManager.cs, MultipleIdpMiddleware.cs
- Focus Areas: Thread safety, error handling, event lifecycle
```

## Usage tips

- **Before**: fetch all inline + issue-level PR comments via `gh api`; read design docs; check for feature-specific PR review guide.
- **During**: cross-reference every finding against existing index — never re-raise as new; use path:line everywhere; tag **[New]** or **[Already raised by: {reviewer}]**; for human rename requests, confirm workspace matches and flag doc/test drift; surface simplification/refactoring with concrete before/after sketches.
- **After**: save full review to `docs/*.md` (required); checkboxes for items needing attention; ask clarifying questions if needed.

## Bad examples

- Findings without path:line
- Finishing only in chat, no Markdown under `docs/`
- Vague feedback without specific recommendations
- Missing critical areas (thread safety, error handling)
- Not checking project standards
- No actionable items / checkboxes
- Raising finding without checking if Copilot/Qodo/human already flagged it
- Summary of findings table missing Source column (Claude / Qodo / Copilot / Human)
- Skipping `gh api` comment-fetch
- Ignoring human rename requests in inline comments
- Overlooking duplication/refactoring opportunities without at least Info-level note
