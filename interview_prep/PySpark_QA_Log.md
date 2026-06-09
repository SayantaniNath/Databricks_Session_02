# PySpark / Spark — Q&A Log

Running log of questions asked during learning sessions, with answers. Newest date at bottom. Refresh anytime.

2026-06-02 — Stage 2B, PySpark SQL (Lesson 3)

Refresh me on lazy vs wide (transformations).

"Wide vs lazy" are two different axes, not opposites.

**Axis 1 — Lazy vs eager (WHEN work happens)**

  * **Transformations are lazy** — `select`, `filter`, `withColumn`, `groupBy`, `join`, `spark.sql("SELECT…")` just record a recipe (build the DAG). Nothing runs.
  * **Actions are eager** — `show()`, `count()`, `collect()`, `write` — trigger the whole recipe to execute.
  * Payoff: Spark sees the full plan before running, so Catalyst optimizes across steps (push filters down, pick join strategy).



**Axis 2 — Narrow vs wide (HOW MUCH data moves across the network)**

  * **Narrow** — each input partition feeds one output partition. No network movement. `select`, `filter`, `withColumn`. Cheap.
  * **Wide** — output partitions pull from many input partitions → **shuffle** (data sent across executors). `groupBy`, `join` (non-broadcast), `orderBy`, `distinct`. Expensive — the #1 thing you tune.
  * A **stage boundary** is exactly where a shuffle happens. Count shuffles → count stages.



**How they combine in Lesson 3:**

Operation| Lazy/eager| Narrow/wide  
---|---|---  
`SELECT … WHERE`| lazy until `.show()`| narrow  
`GROUP BY`| lazy until `.show()`| **wide** (shuffle)  
`ORDER BY`| lazy until `.show()`| **wide** (shuffle)  
`JOIN`| lazy until `.show()`| **wide** — unless broadcast (tiny `coin_meta` → BroadcastHashJoin, no shuffle)  
  
Full reference: `~/Downloads/Spark_Architecture_Walkthrough.html`

* * *

What does this do? `spark = (SparkSession.builder.appName("…").getOrCreate())`

It creates (or reuses) the SparkSession — the entry point every DataFrame/SQL call goes through.
    
    
    spark = (
        SparkSession.builder              # a configurator to set up a session
        .appName("FinFlow_Lesson3_SQL")   # name shown in Spark UI (localhost:4040)
        .getOrCreate()                    # build it — or hand back the existing one
    )

  * **`SparkSession.builder`** — a configurator you chain settings onto (app name, configs, master URL). Nothing exists yet.
  * **`.appName(...)`** — labels the application; purely for identification in the Spark UI and logs.
  * **`.getOrCreate()`** — the actual build. "Get" the active session if one exists in this process, else "create" one. A JVM allows only one active session, so re-running won't spin up duplicates or error.



**What you get back (`spark`):** the handle that owns `spark.read.json(...)`, `spark.sql("…")`, and launches the Driver + Spark UI on `localhost:4040`. This `spark` object _is_ the Driver's entry point — builds the DAG, hands tasks to executors. Creating it is setup, not an action — nothing computes here.

The outer parentheses are just Python letting you split a chained call across lines for readability — no Spark meaning.

* * *

Why is the path wrapped in `str(...)`? `DATA = str(Path.home() / "Downloads" / … / "sample.jsonl")`

Because `Path.home() / "…"` produces a PosixPath object, and Spark's reader wants a plain **string**.

  * **`Path.home()`** → a `Path` object (`/Users/sayantaninath`).
  * **`/ "Downloads" / …`** → the `/` operator is overloaded on `Path` to join segments. Still a `Path`, not text. (Readable, OS-agnostic joins — the nice part of `pathlib`.)
  * **`str(...)`** → flattens it into the real string `"/Users/sayantaninath/Downloads/…/sample.jsonl"`.



**Why Spark needs the string:** `spark.read.json(path)` hands the path **across to the JVM** (Spark's engine is Scala/Java). The JVM doesn't understand a Python `PosixPath` — it expects a Java string. Pure-Python libs like `pandas.read_json` accept a `Path` directly (they honor `os.PathLike`); the Python→JVM boundary doesn't, so you convert explicitly. Skip the `str()` and you'd likely hit a `py4j` type error.

**Pattern:** use `pathlib` to build the path readably, wrap in `str()` at the moment you hand it to Spark.
    
    
    p = Path.home() / "Downloads"
    print(type(p))        # <class 'pathlib.PosixPath'>
    print(type(str(p)))   # <class 'str'>

* * *

What's the alternative to `show(n)` to show ALL records?

`df.show()` defaults to 20 rows and truncates long columns at 20 chars. To show all:
    
    
    df.show(df.count())                 # pass the exact row count as n
    df.show(df.count(), truncate=False) # + full untruncated column values

Method| Returns| When to use  
---|---|---  
`df.show(df.count())`| prints, nothing returned| quick visual scan of all rows  
`df.collect()`| Python list of Row objects| pull data to driver to loop/process  
`df.toPandas()`| pandas DataFrame| nicer display (notebooks), pandas ops  
  
⚠️ The catch: all three pull every row to the Driver — an **action** that can blow up driver memory or hang on a big table. Fine on 6 rows, dangerous in production. `df.show(20)` exists so you peek cheaply without dragging the whole dataset back.

`truncate=False` is the flag you'll reach for most — keeps timestamps and names from being cut off.

* * *

Difference between using the DataFrame API and Spark SQL?

Two front-ends to the same engine — no performance difference. Both compile through the same Catalyst optimizer to the same physical plan.
    
    
    # DataFrame API
    df.select("coin", "price_usd").filter(F.col("price_usd") > 1000)
    
    # Spark SQL — identical result, identical plan
    spark.sql("SELECT coin, price_usd FROM prices WHERE price_usd > 1000")

Run `.explain()` on both → same physical plan (that's Ex 10 in Lesson 3).

**Why have both? About how you write/read code, not speed:**

| DataFrame API| Spark SQL  
---|---|---  
Looks like| Python method chaining| SQL strings  
Errors caught| compile/build time (bad method name fails immediately)| runtime (bad SQL fails only when query runs)  
Composability| great — build `df` step by step, reuse, pass to functions| weaker — string concatenation gets ugly  
Complex logic readability| nested chains get hard to read| complex joins/aggs often read cleaner  
Who reaches for it| Python engineers, programmatic pipelines| analysts, SQL-first, ad-hoc queries  
IDE support| autocomplete, type hints| just a string — no help  
  
**Guidance:** DataFrame API for dynamically-built logic (loops/conditionals/reusable fns) or compile-time safety; Spark SQL for gnarly multi-join/aggregation queries that read cleaner as SQL or SQL-fluent collaborators. **Mix freely** — `createOrReplaceTempView` flips a DataFrame into SQL and back (common: heavy transforms in the API, final aggregation in SQL).

Interview takeaway: "Same engine, same Catalyst plan, same performance — choice is readability, composability, and compile-time vs runtime error checking." Proving equivalence with `.explain()` is what they're testing.

* * *

What is Iceberg, Hudi, Trino?

Iceberg & Hudi are table formats; Trino is a query engine — different layers of the stack.

**The problem they exist for:** a raw data lake is just Parquet files in object storage (S3). Files alone give no transactions, no time travel, no safe concurrent writes. The lakehouse stack fixes that.

**Table formats — Iceberg & Hudi (and Delta)** — a metadata layer on top of Parquet files that turns a pile of files into a real table with: ACID transactions, time travel (query old snapshots), schema evolution, and MERGE/upserts/deletes.

Format| Born at| Sweet spot| Ecosystem  
---|---|---|---  
Delta| Databricks| tight Databricks/Spark integration| Databricks  
Iceberg| Netflix| huge tables, engine-neutral, hidden partitioning| Apple, Netflix, Snowflake, AWS — momentum winner  
Hudi| Uber| streaming upserts, CDC, incremental pulls| Uber, Robinhood  
  
Same problem; differences are partition handling, how updates are stored, and which engines/vendors back them.

**Trino** — a distributed SQL query engine (formerly PrestoSQL), _not_ a storage format. Doesn't store data; runs fast SQL _across_ data wherever it lives. Superpower: **federation** — one query can join S3 (Iceberg/Hudi/Delta) + PostgreSQL + MySQL. "The SQL brain you point at many sources," vs Spark which is more a general compute/ETL engine.

Interview takeaway: table format (Delta/Iceberg/Hudi) = ACID + time travel on lake files; query engine (Trino, Spark SQL, Athena) = runs SQL over them. "Why Iceberg?" → engine-neutral + scales to massive tables + industry momentum. "Why Delta?" → best if all-in on Databricks.

## show() vs display()

Q: What is the difference between `show()` and `display()` in Spark?

**Both show data from a DataFrame — but they work in different environments.**

`show()` — PySpark, works anywhere
    
    
    df.show()                  # first 20 rows (default)
    df.show(5)                 # first 5 rows
    df.show(truncate=False)    # don't cut off long strings

Output is plain text in the terminal or console.

`display()` — Databricks notebooks only
    
    
    display(df)

Output is a rich interactive table — sortable columns, filter, chart view (bar/line/pie), download as CSV. Not available outside Databricks.

| show()| display()  
---|---|---  
Works in| Anywhere (terminal, script, notebook)| Databricks notebooks only  
Output| Plain text table| Interactive UI table  
Charts| ❌ No| ✅ Yes — built-in  
Truncates long strings| Yes (use truncate=False to disable)| No — shows full content  
Use in production scripts| ✅ Yes| ❌ No  
  
Rule: In Databricks → `display()`. In a local script or terminal → `show()`.

## PySpark vs Flink vs Presto/Trino — when to use which

Q: When do you use PySpark vs Flink vs Presto/Trino?

| PySpark| Flink| Presto/Trino  
---|---|---|---  
Best for| Batch ETL, ML, large-scale transforms| True real-time streaming (sub-second)| Fast ad-hoc SQL on existing data  
Processing model| Micro-batch or batch| Continuous, event-by-event| Query engine only — no pipeline  
Latency| Seconds to minutes| Milliseconds to seconds| Seconds (query time)  
Stores data?| No| No| No — queries data where it lives  
Typical use| DW pipelines, Delta Lake, feature engineering| Fraud detection, real-time alerts, CDC| BI dashboards, cross-source federation  
  
**PySpark** — data is large, you need transformations + joins + aggregations, seconds of latency is fine. 90% of DE work.

**Flink** — true sub-second real-time needed (fraud scoring per transaction as it happens). More operationally complex than Spark Streaming.

**Presto/Trino** — data already exists in S3/Delta/Iceberg/Postgres and you want fast SQL without moving it. Superpower: federation — one query across multiple sources.

Interview one-liner: PySpark = batch/streaming ETL engine. Flink = true real-time streaming engine. Presto/Trino = fast SQL query engine across existing data stores. They solve different problems and often coexist in the same stack.
