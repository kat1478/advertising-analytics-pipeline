# Git Workflow

## Branch roles

```text
master   → stable portfolio release
develop  → integration branch
feature/* → one task per branch
```

## Initial setup

```bash
git init
git checkout -b master
git add .
git commit -m "chore(repo): initialize portfolio project governance"
git checkout -b develop
git push -u origin master
git push -u origin develop
```

## New task flow

Start from `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/001-project-scaffold
```

Work in small commits:

```bash
git add <files>
git commit -m "feat(repo): add project scaffold"
```

Push and open PR to `develop`:

```bash
git push -u origin feature/001-project-scaffold
```

## Release flow

When `develop` is ready:

```bash
git checkout develop
git pull origin develop
git checkout -b release/v0.1.0
```

Create a PR from `release/v0.1.0` to `master`.

After merge, tag the release:

```bash
git checkout master
git pull origin master
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

## Protected branches

Recommended branch protection for `master`:

- require pull request before merging;
- require status checks to pass;
- require code owner review;
- block force pushes;
- block deletions.

Recommended branch protection for `develop`:

- require pull request before merging;
- require status checks to pass;
- block force pushes;
- block deletions.
