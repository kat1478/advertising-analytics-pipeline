# Git Workflow

## Branch roles

```text
master   → stable portfolio release
develop  → integration branch
feature/* → one task per branch
```

## New task flow

Start from `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/012-next-feature
```

Work in small, focused commits:

```bash
git add <files>
git commit -m "feat(area): describe the change"
```

Push and open a PR to `develop`:

```bash
git push -u origin feature/012-next-feature
```

PRs are reviewed and merged into `develop`.

## Release flow

When `develop` is ready for a portfolio release:

1. Merge `develop` into `master` via a release PR.
2. After merge, tag the release on `master`:

```bash
git checkout master
git pull origin master
git tag -a v0.5.0 -m "Release v0.5.0"
git push origin v0.5.0
```

## Protected branches

Recommended branch protection for `master`:

- require pull request before merging
- require status checks to pass
- block force pushes
- block deletions

Recommended branch protection for `develop`:

- require pull request before merging
- require status checks to pass
- block force pushes
- block deletions
