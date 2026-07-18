# Continuous Integration

The project uses GitHub Actions for automated testing and end-to-end pipeline validation.

## Triggers

The CI workflow runs on:
- pushes to `develop` or `master`
- pull requests targeting `develop` or `master`
- manual runs via `workflow_dispatch`

Concurrent runs on the same branch are automatically cancelled to avoid queuing stale builds.

## Workflow overview

Workflow file: [.github/workflows/ci.yml](../.github/workflows/ci.yml)

```
push / pull_request → tests job → end-to-end job
```

## Job 1: `tests`

**Runner**: `ubuntu-latest`  
**Timeout**: 20 minutes

| Step | Command |
|---|---|
| Environment setup | `mamba-org/setup-micromamba@v2` from `environment.yml` |
| Compile check | `python -m compileall src tests scripts` |
| Test suite | `python -m pytest -q` |

If `tests` fails, the `end-to-end` job is skipped.

## Job 2: `end-to-end`

**Runner**: `ubuntu-latest`  
**Timeout**: 30 minutes  
**Depends on**: `tests`

| Step | Command |
|---|---|
| Environment setup | `mamba-org/setup-micromamba@v2` (shared cache with job 1) |
| Run pipeline | `python -m src.run_pipeline` |
| Verify outputs | `python scripts/verify_pipeline_outputs.py` |
| Deterministic diff check | `git diff --exit-code reports/campaign_report.md reports/analytics_insights.md` |
| Upload report artifacts | `actions/upload-artifact@v4` → `pipeline-reports` (30-day retention) |

## Deterministic artifact check

The committed `reports/campaign_report.md` and `reports/analytics_insights.md` are regenerated from scratch by `run_pipeline` in CI.  
After generation, `git diff --exit-code` verifies that the regenerated content exactly matches the committed files.

If this step fails:
1. Code changed in a way that affects the report output.
2. Regenerate locally: `python -m src.run_pipeline`
3. Commit the updated reports before merging.

This check detects non-determinism and uncommitted output changes. No dynamic runtime timestamps are embedded in the reports (deterministic dataset metadata is used instead).

## CI Artifacts

After each successful `end-to-end` run, two report files are uploaded as CI artifacts:
- `reports/campaign_report.md`
- `reports/analytics_insights.md`

Artifacts are retained for 30 days and are available for download from the Actions run page.

## Environment and caching

Dependencies are managed entirely through `environment.yml` using `mamba-org/setup-micromamba`.  
Both the conda environment and downloaded packages are cached to speed up repeat runs.  
`pip install` is never invoked manually.

## Permissions

The workflow uses `permissions: contents: read` only.  
It does not write to the repository, create branches, or commit any files during CI.

## Actions used

| Action | Version | Purpose |
|---|---|---|
| `actions/checkout` | v4 | Repository checkout |
| `mamba-org/setup-micromamba` | v2 | Conda/mamba environment setup |
| `actions/upload-artifact` | v4 | Upload report files |
