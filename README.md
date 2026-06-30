# DE Interview Prep — Spark · Delta Lake · Kafka · Python

Personal study repo for FAANG / Databricks Data Engineer interview preparation.  
**Target:** Job-ready by Oct 1, 2026.  
**Stack:** PySpark, Delta Lake, Kafka, Airflow, dbt, Snowflake, AWS, Python.

---

## Repo Structure

```
.
├── finflow/                        # PySpark/Pandas learning sandbox (not a portfolio project)
│   ├── ingestion/                  # Kafka producers — crypto prices, stock ticks
│   ├── consumers/                  # Kafka consumer — raw event reader
│   ├── cache/                      # Redis manager (TTL-based caching layer)
│   ├── dbt/models/                 # dbt staging + mart models (Snowflake target)
│   │   ├── staging/                # stg_crypto_prices, stg_stock_prices
│   │   └── marts/                  # fact_price_movements, agg_daily_summary
│   ├── airflow/dags/               # finflow_dag.py — Airflow orchestration skeleton
│   ├── data/raw/                   # Sample JSONL data (crypto, merchants)
│   ├── practice_01–04.py           # PySpark core API exercises
│   ├── practice_pandas_*.py        # Pandas DE exercises (lessons 1–6)
│   ├── practice_pyspark_lesson*.py # PySpark DataFrame API (lessons 1–3)
│   ├── practice_spark_salting.py   # Skew detection + salting (join + groupBy)
│   └── requirements.txt            # kafka-python, pyspark, dbt-snowflake, airflow, redis, boto3
│
├── interview_prep/
│   ├── Spark_Architecture_Walkthrough.html   # Driver/Executor/DAG/Catalyst/Tungsten/AQE
│   ├── Spark_UI_Walkthrough.html             # Spark UI: stages, tasks, shuffle read/write
│   ├── Spark_Data_Ingestion_Guide.html       # Auto Loader, COPY INTO, Structured Streaming
│   ├── Spark_Master_Checklist.html           # Quick-reference: internals, joins, caching, skew
│   ├── PySpark_QA_Log.html                   # Running Q&A log — concepts + answers
│   ├── python_de_foundations.py              # Python DE exercises: generators, chunked I/O, memory
│   ├── neetcode_practice.py                  # NeetCode 150 — Arrays & Hashing, Two Pointers, etc.
│   ├── python_log.md                         # NeetCode session log
│   └── sd_qa_log.md                          # System design Q&A log
│
├── LEARNING_PATH.md                # Full Phase 1 plan with status per topic
├── Learning_Plan_Full.html         # HTML version of the same plan
├── Databricks_DEA_Learning_Resources.html    # DEA cert resource map (books, YouTube, docs)
├── HIPAA_for_Data_Engineers_Healthmap_Prep.html  # HIPAA Safe Harbor + GDPR for DE roles
├── SQL_Advanced_Window_Functions_Guide.html  # Window functions, CTEs, dedup, SCD patterns
├── Project_Databricks_Lakehouse_Blueprint.html   # Medallion + DLT + Unity Catalog design doc
├── Project_Fraud_Detection_Blueprint.html    # Kafka → Structured Streaming → MLflow → Delta
├── Project_FinFlow_Prep.html                 # FinFlow pipeline design notes
├── Project_AI_Job_Agent_Prep.html            # AI job agent architecture notes
└── Project_Interview_Prep.html               # Interview round breakdown + per-company notes
```

---

## What Each Folder Contains

### `finflow/`
PySpark and Pandas exercises built around a synthetic financial events pipeline (crypto + stock ticks). Used to practice:
- Spark DataFrame API: `select`, `filter`, `join`, `groupBy`, `agg`, `withColumn`
- Skew detection via `spark_partition_id()` and salting (join salting + two-pass groupBy)
- Kafka event ingestion (producer/consumer pattern with `kafka-python`)
- Pandas DE patterns: `read_csv(chunksize=)`, `dtype` downcasting, `groupby/agg/merge`
- dbt models on Snowflake: staging → marts, incremental materialization
- Airflow DAG skeleton for pipeline orchestration

> **Note:** This is a learning sandbox, not a portfolio project. The production-grade portfolio projects (AWS ClinicalFlow Healthcare Lakehouse, Fraud Detection Pipeline, CDC Pipeline, Databricks Lakehouse + AI Monitor) live in separate repos.

### `interview_prep/`
Reference documents and practice files keyed to Databricks/FAANG DE interview rounds:

| File | Covers |
|---|---|
| `Spark_Architecture_Walkthrough.html` | Driver/Executor model, partitions, DAG, Catalyst 4-phase optimizer, Tungsten off-heap + WSCG, AQE (coalescing, dynamic join switching, skew join), shuffle mechanics, repartition vs coalesce, caching storage levels |
| `Spark_UI_Walkthrough.html` | Reading stage timelines, task distribution, shuffle read/write metrics, skew detection (min/median/max task sizes), BHJ vs SMJ in physical plan |
| `Spark_Data_Ingestion_Guide.html` | Auto Loader (directory listing vs file notification), COPY INTO, Structured Streaming micro-batch model |
| `Spark_Master_Checklist.html` | Quick-reference: join strategies (BHJ/SMJ/SHJ thresholds), caching gotchas, salting formula, AQE flags |
| `PySpark_QA_Log.html` | Accumulated Q&A from Spark sessions — interview-style Qs + verified answers |
| `python_de_foundations.py` | Generator functions, `yield` vs `return`, generator expressions, chunked file reader with `itertools.islice`, memory-efficient patterns |
| `neetcode_practice.py` | Arrays & Hashing pattern (Two Sum, Group Anagrams, Top K Frequent, etc.) |
| `sd_qa_log.md` | System design questions + answers (Prepaid Credits / billing ledger, Design LeetCode submission pipeline) |

---

## Learning Plan Status

See [`LEARNING_PATH.md`](LEARNING_PATH.md) for the full phase-by-phase plan with ✅/🟡/⏳ status per topic.

**Phase 1 pillars (Jun–Oct 2026):**
1. SQL + Python Coding (CodeSignal / Algorithm rounds)
2. Spark + Databricks depth — Architecture ✅ · Internals ✅ · Delta Lake ✅ · Structured Streaming 🟡 · DLT · Unity Catalog · Auto Loader · MLflow
3. Concurrency round (Databricks-specific — threading primitives, thread-safe data structures)
4. DE Core — Kafka · Airflow · Snowflake · dbt
5. System Design — DDIA reading + case studies + out-loud mocks
6. Certifications — AWS CCP (Jul 2026) · Databricks DEA (Aug 2026) · SnowPro Core (Sep 2026)
7. Projects — AWS ClinicalFlow ✅ Phase 1 · Fraud Detection · CDC Pipeline · Databricks Lakehouse + AI Monitor
8. Behavioral stories (Aug 2026)

---

## Key Technical Concepts Covered

**Spark internals:** Catalyst optimizer (Analysis → Logical Opt → Physical Planning → Codegen), Tungsten whole-stage code generation, AQE partition coalescing + dynamic join switching + skew join, shuffle map/reduce mechanics, broadcast join auto-threshold (10MB default, 50MB config), salting for skewed joins and groupBy aggregations, Photon vectorized C++ execution engine.

**Delta Lake:** `_delta_log` JSON commit files + Parquet checkpoints at every 10th commit, ACID via optimistic concurrency control, time travel via log replay, schema enforcement vs `mergeSchema`, OPTIMIZE + Z-ORDER + liquid clustering, VACUUM retention horizon, MERGE INTO isolation level + write amplification, Change Data Feed (pre/post-image), small files problem, dynamic file pruning + min/max column statistics.

**Python DE:** Generator functions and expressions, lazy pipelines with `itertools.islice`, chunked I/O patterns, memory-efficient Pandas (`chunksize`, `dtype` downcasting, `memory_usage()`).

---

## Environment

```bash
# Python virtualenv (Python 3.14.4)
source ~/myenv/bin/activate

# Run a practice file
python finflow/practice_spark_salting.py
python interview_prep/python_de_foundations.py
```
