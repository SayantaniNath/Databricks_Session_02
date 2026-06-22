# FinFlow — Learning Sandbox

> **Status: Learning sandbox — not a portfolio project.**
> Skills demonstrated here are superseded by [AWS ClinicalFlow](../LEARNING_PATH.md) and the Databricks Lakehouse capstone.

This directory contains PySpark, Pandas, and pipeline skeleton code written during the DE interview prep learning plan (May–Jun 2026). It is preserved as a reference for exercises and patterns practiced during study sessions.

---

## What's here

### Practice files (learning exercises)
| File | Topic | Pillar |
|---|---|---|
| `practice_pyspark_lesson1.py` | Spark Architecture + first DataFrame ops (select, filter, join, groupBy) | 2A/2B |
| `practice_pyspark_lesson2.py` | Advanced DataFrame API (withColumn, window functions, agg) | 2B |
| `practice_pyspark_lesson3.py` | PySpark SQL — createOrReplaceTempView, spark.sql, Catalyst plan | 2B |
| `practice_spark_salting.py` | Spark UI hands-on — skew detection + join/groupBy salting | 2B |
| `practice_pandas_lesson2-6.py` | Pandas transformations, merges, reshaping, time series | P1 |
| `practice_01-04.py` | Early Python/data exercises | P1 |

### Pipeline skeleton (incomplete)
| Directory | What it is |
|---|---|
| `ingestion/` | Crypto price producer (CoinGecko API) + stock producer — skeleton only |
| `consumers/` | Kafka raw consumer — skeleton |
| `cache/` | Redis manager for price TTL caching — skeleton |
| `dbt/models/` | Staging + marts SQL for crypto/stock prices — not wired end-to-end |
| `airflow/dags/` | Airflow DAG skeleton — not deployed |
| `data/raw/` | Synthetic crypto price JSONL (sample data for exercises) |

### Why not completed
The pipeline was originally designed around crypto price data. During planning (Jun 2026), the portfolio strategy was updated:
- **AWS ClinicalFlow** (Synthea EHR, HIPAA/GDPR) covers batch ETL, Delta/Iceberg, MWAA orchestration, data quality
- **Databricks Lakehouse capstone** covers Delta Lake, DLT, Unity Catalog end-to-end
- FinFlow's intended skills are fully covered by those two projects with a stronger data story

---

## Data
`data/raw/crypto/` — synthetic crypto price JSON (no real API data, no credentials).
`config.py` reads all secrets from environment variables — no hardcoded credentials.
