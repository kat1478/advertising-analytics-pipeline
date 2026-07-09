# Contributing Guidelines

This repository is maintained as a professional portfolio project. The goal is to keep the public history clean, readable, and recruiter-friendly.

## Branching model

- `master` is stable and should contain only reviewed releases.
- `develop` is the integration branch.
- Every task uses a dedicated branch from `develop`.

Branch naming:

```text
feature/<ticket-number>-<short-description>
fix/<ticket-number>-<short-description>
docs/<ticket-number>-<short-description>
test/<ticket-number>-<short-description>
refactor/<ticket-number>-<short-description>
```

Examples:

```text
feature/001-project-scaffold
feature/002-synthetic-data-generator
fix/008-safe-division-roas
```

## Commit style

Use small, focused commits. Prefer Conventional Commits:

```text
feat(data): add synthetic campaign generator
feat(sql): build daily campaign performance mart
test(metrics): add safe division tests
docs(readme): document pipeline architecture
ci(github): add pytest workflow
```

## Pull request rules

Each pull request should:

1. Solve one task only.
2. Include a clear summary.
3. Include validation steps.
4. Keep generated local data and private agent files out of the diff.
5. Pass CI before merge.
6. Target `develop`, except release PRs from `develop` to `master`.

## Definition of Done

A task is done when:

- code is implemented and formatted;
- relevant tests are added or updated;
- pipeline behavior is documented when needed;
- generated files are not accidentally committed;
- CI passes;
- the PR description explains what changed and why.
