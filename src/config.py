PROJECT_NAME = "Advertising Analytics Data Pipeline"
DEFAULT_DATABASE_NAME = "ads.duckdb"
DEFAULT_RANDOM_SEED = 42

# Currency
CURRENCY_CODE = "PLN"
CURRENCY_SYMBOL = "zł"

# Reporting dataset metadata (deterministic, used instead of runtime timestamps)
DATASET_SEED = DEFAULT_RANDOM_SEED
REPORTING_PERIOD = "2023-06-01 – 2023-06-30"

# Classification thresholds for analytics assistant and report
# These are absolute floors that prevent extreme ROAS values from distorting relative comparisons.
# Used in combination with dataset-relative percentiles where noted.
LOW_ROAS_THRESHOLD = 1.5       # Below this → weak performance
HIGH_ROAS_THRESHOLD = 3.0      # Above this → strong performance
EXCEPTIONAL_ROAS_THRESHOLD = 5.0  # Above this → exceptional performance

LOW_CVR_THRESHOLD = 0.05       # Below this (5%) → low conversion rate
HIGH_CPC_THRESHOLD = 5.0       # Above this (5 PLN/click) → expensive traffic
