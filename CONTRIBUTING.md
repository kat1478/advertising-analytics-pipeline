# Contributing Guidelines

## Branching Strategy
1. The `develop` branch is the main integration branch.
2. The `master` branch contains the release-ready code. No direct commits to `master`.
3. Create feature branches from `develop` following this naming convention: `feature/<task-id>-<description>` or `docs/<task-id>-<description>`.
4. Keep PRs small and focused on a single task.

## Commit Rules
1. Follow Conventional Commits format (e.g., `feat: ...`, `fix: ...`, `chore: ...`, `docs: ...`).
2. Write clear and descriptive commit messages.
3. Ensure no private files (e.g., `.agent-private/`, `.agents/`) or secrets are committed.

## Pull Requests
1. All changes must be made via Pull Requests.
2. Ensure tests pass before merging.
3. Require documentation updates when behavior or architecture changes.
