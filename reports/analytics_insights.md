# Analytics Assistant Insights

*(Rule-based analytics assistant. No external LLM APIs were used. Classifications are deterministic and based on fixed thresholds — see [docs/REPORTING.md](../docs/REPORTING.md).)*

**Dataset Seed:** 42  
**Reporting Period:** 2023-06-01 – 2023-06-30  
**Currency:** PLN (zł)

## Threshold Reference

| Threshold | Value |
|-|-|
| Weak ROAS (< ) | 1.5 |
| Strong ROAS (> ) | 3.0 |
| Exceptional ROAS (> ) | 5.0 |
| Low CVR (< ) | 5% |
| High CPC (> ) | 5.0 zł |

## Campaign Insights

### 🔴 Critical

- **Campaign_12** — Critical: High spend (477.12 zł) with weak ROAS (0.72). Campaign is burning budget with low return. Review or pause to prevent further loss.

### 🟢 Opportunity

- **Campaign_1** — Opportunity: Strong ROAS (3.17). Campaign performs well. Monitor for saturation before scaling.
- **Campaign_10** — Opportunity: Exceptional ROAS (21.88). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_11** — Opportunity: Exceptional ROAS (16.27). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_13** — Opportunity: Exceptional ROAS (7.98). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_14** — Opportunity: Exceptional ROAS (12.99). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_16** — Opportunity: Exceptional ROAS (7.94). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_17** — Opportunity: Exceptional ROAS (8.22). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_18** — Opportunity: Exceptional ROAS (10.17). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_19** — Opportunity: Exceptional ROAS (13.05). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_2** — Opportunity: Exceptional ROAS (22.95). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_20** — Opportunity: Exceptional ROAS (14.33). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_3** — Opportunity: Exceptional ROAS (13.39). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_4** — Opportunity: Exceptional ROAS (7.08). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_5** — Opportunity: Exceptional ROAS (5.42). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_6** — Opportunity: Exceptional ROAS (16.16). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_7** — Opportunity: Strong ROAS (4.87). Campaign performs well. Monitor for saturation before scaling.
- **Campaign_8** — Opportunity: Exceptional ROAS (7.73). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_9** — Opportunity: Exceptional ROAS (8.95). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.

## Category Insights

### Opportunities

- **Clothing**: ROAS 5.64 — strong category performance. Consider increasing product coverage and ad investment.
- **Electronics**: ROAS 8.02 — strong category performance. Consider increasing product coverage and ad investment.
- **Home**: ROAS 11.00 — strong category performance. Consider increasing product coverage and ad investment.
- **Sports**: ROAS 8.17 — strong category performance. Consider increasing product coverage and ad investment.
- **Toys**: ROAS 6.24 — strong category performance. Consider increasing product coverage and ad investment.

## Limitations

- Insights use absolute thresholds from `src/config.py` combined with dataset-relative context (e.g. median campaign cost).
- Based on synthetic data only — findings do not reflect real campaign behaviour.
- The assistant does not model externalities such as seasonality, creative quality, or competitive pressure.