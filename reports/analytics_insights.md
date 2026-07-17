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

- **Campaign_1** — Critical: High spend (1,143.44 zł) with weak ROAS (1.33). Campaign is burning budget with low return. Review or pause to prevent further loss.
- **Campaign_12** — Critical: High spend (1,141.34 zł) with weak ROAS (0.30). Campaign is burning budget with low return. Review or pause to prevent further loss.

### 🟢 Opportunity

- **Campaign_10** — Opportunity: Exceptional ROAS (15.79). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_11** — Opportunity: Exceptional ROAS (11.10). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_13** — Opportunity: Exceptional ROAS (5.29). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_14** — Opportunity: Exceptional ROAS (9.71). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_16** — Opportunity: Exceptional ROAS (5.35). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_17** — Opportunity: Exceptional ROAS (5.67). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_18** — Opportunity: Exceptional ROAS (6.56). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_19** — Opportunity: Exceptional ROAS (19.12). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_2** — Opportunity: Exceptional ROAS (15.91). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_20** — Opportunity: Strong ROAS (4.17). Campaign performs well. Monitor for saturation before scaling.
- **Campaign_3** — Opportunity: Exceptional ROAS (9.97). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_4** — Opportunity: Strong ROAS (3.03). Campaign performs well. Monitor for saturation before scaling.
- **Campaign_5** — Opportunity: Strong ROAS (3.61). Campaign performs well. Monitor for saturation before scaling.
- **Campaign_6** — Opportunity: Strong ROAS (4.59). Campaign performs well. Monitor for saturation before scaling.
- **Campaign_7** — Opportunity: Strong ROAS (3.35). Campaign performs well. Monitor for saturation before scaling.
- **Campaign_8** — Opportunity: Exceptional ROAS (5.56). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.
- **Campaign_9** — Opportunity: Exceptional ROAS (6.44). This campaign generates outstanding revenue relative to cost. Candidate for careful budget increase.

## Category Insights

### Opportunities

- **Clothing**: ROAS 3.08 — strong category performance. Consider increasing product coverage and ad investment.
- **Electronics**: ROAS 4.34 — strong category performance. Consider increasing product coverage and ad investment.
- **Home**: ROAS 6.00 — strong category performance. Consider increasing product coverage and ad investment.
- **Sports**: ROAS 4.49 — strong category performance. Consider increasing product coverage and ad investment.
- **Toys**: ROAS 3.42 — strong category performance. Consider increasing product coverage and ad investment.

## Limitations

- Insights use absolute thresholds from `src/config.py` combined with dataset-relative context (e.g. median campaign cost).
- Based on synthetic data only — findings do not reflect real campaign behaviour.
- The assistant does not model externalities such as seasonality, creative quality, or competitive pressure.