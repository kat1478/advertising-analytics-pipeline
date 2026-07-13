# Changelog

## Release v0.3

This release introduces the SQL staging layer, analytical marts, advertising metric definitions and robust metric quality tests.

### Included
- SQL staging transformations
- Analytical dimensions and fact table
- Daily campaign performance mart
- Category performance mart
- Advertising metrics:
  - CTR
  - CPC
  - conversion rate
  - ROAS
  - cost per conversion
- Impression-based attribution model for daily funnel consistency
- Metric quality checks for non-negativity, ratio bounds and duplicate prevention
- Metrics documentation in `docs/METRICS.md`

### Validation
- python -m compileall src tests
- python -m pytest -q
- python -m src.generate_data
- python -m src.load_raw
- python -m src.validate_data
- python -m src.run_sql

### Not included yet
- Markdown report
- Analytics assistant
- Dashboard
