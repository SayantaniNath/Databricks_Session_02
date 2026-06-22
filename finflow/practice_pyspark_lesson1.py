"""
Stage 2B Lesson 1 — Spark Architecture + First DataFrame Ops
Practice file (write from blank, OR read the theory blocks first if tired).

Data: ~/Downloads/finflow/data/raw/crypto/sample.jsonl
Columns: coin, symbol, price_usd, fetched_at
"""

# ===================================================================
# THEORY 1 — What is Spark, really?
# ===================================================================
#
# Spark is a DISTRIBUTED compute engine. You write code that LOOKS
# like Pandas, but it runs across many machines in parallel.
#
# The pieces:
#
#   Driver           — your Python process. Runs your code, builds
#                      the execution plan, ships work to executors.
#                      One per Spark application.
#
#   Executors        — JVM processes that DO the work. Each one
#                      processes a slice of data ("partition").
#                      Cluster has many of these.
#
#   Cluster Manager  — assigns executors to your app (YARN, K8s,
#                      Databricks, or "local" mode for laptops).
#
#   SparkSession     — the entry point in your code. Holds the
#                      connection to the cluster.
#
# On your laptop today: driver + executors all run inside ONE JVM
# (this is called "local mode"). You won't see the full power until
# Databricks. But the API and concepts are identical.

# ===================================================================
# THEORY 2 — Lazy evaluation (the single most important concept)
# ===================================================================
#
# In Pandas: every line of code runs immediately.
# In Spark: most operations RECORD the intent and run NOTHING.
#
# Two categories of operations:
#
#   Transformations  — build the plan. NOTHING runs yet.
#                      select, filter, groupBy, join, withColumn, etc.
#
#   Actions          — trigger the plan. Spark runs everything queued.
#                      show(), count(), collect(), write.*, toPandas()
#
# Why? Spark uses the time between transformations to OPTIMIZE the
# whole plan (push filters down, combine projections, choose join
# strategy). Pandas can't do this — every line is final.
#
# Mental model:
#   df.filter(...).select(...).groupBy(...).agg(...)   ← still nothing has run
#   .show()                                            ← NOW Spark runs everything

# ===================================================================
# THEORY 3 — DAG (Directed Acyclic Graph)
# ===================================================================
#
# Every chain of transformations becomes a DAG — a graph of steps
# that depend on each other.
#
#   df = spark.read.json(...)        ← node 1
#   df2 = df.filter(...)             ← node 2, depends on node 1
#   df3 = df2.select(...)            ← node 3, depends on node 2
#   df3.count()                      ← action — Spark walks the DAG
#
# Spark sees the WHOLE DAG before running, so it can:
#   - skip unused columns (column pruning)
#   - push filters before joins (predicate pushdown)
#   - pick the best join algorithm
#
# You'll see this DAG in the Spark UI later (port 4040 by default).


# ===================================================================
# HANDS-ON — only proceed if you have energy after the theory above
# ===================================================================

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pathlib import Path

# Create a SparkSession — your entry point.
# .appName() names this app (shows up in the Spark UI).
# .getOrCreate() reuses an existing session if there is one.
spark = (
    SparkSession.builder
    .appName("FinFlow_Lesson1")
    .getOrCreate()
)

DATA = str(Path.home() / "Downloads" / "finflow" / "data" / "raw" / "crypto" / "sample.jsonl")

# Note: spark.read.json() can read JSON Lines (one JSON object per line).
df = spark.read.json(DATA)


# -------------------------------------------------------------------
# BLOCK 1 — Inspect the DataFrame
# -------------------------------------------------------------------
#
# Three quick-look methods (similar to Pandas):
#   df.show(n)          → prints first n rows in a nice table (default n=20)
#   df.printSchema()    → prints column names and dtypes (like df.dtypes)
#   df.columns          → list of column names
#   df.count()          → row count (this is an ACTION — triggers execution)


# Ex 1. Print the first 10 rows of df using .show().
# Your code:

df.show(10)

# Ex 2. Print the schema (column names + types) using .printSchema().
# Your code:

df.printSchema()


# Ex 3. Print the row count using .count().
# Your code:

print(df.count())

# -------------------------------------------------------------------
# BLOCK 2 — select + filter (the bread and butter)
# -------------------------------------------------------------------
#
#   df.select("col1", "col2")               → pick columns
#   df.select(F.col("col1"), F.col("col2")) → same, using the F.col helper
#   df.filter(F.col("price_usd") > 1000)    → row filter
#   df.filter("price_usd > 1000")           → same, SQL-string form
#
# Note: both forms work; F.col() is preferred for complex expressions.
# Remember — these are TRANSFORMATIONS. Nothing runs until you call
# an action like .show().


# Ex 4. Select only the `coin` and `price_usd` columns. Show the result.
# Your code:

df.select(F.col("coin"), F.col("price_usd")).show(10)


# Ex 5. Filter to rows where price_usd > 1000. Show the result.
#       (Should drop the solana rows.)
# Your code:

df.filter(F.col("price_usd")>1000).show(10)

# Ex 6. Chain both: select `coin` + `price_usd`, then filter price > 1000.
#       Show the result. (One chained statement, no intermediate variable.)
# Your code:

df.select(F.col("coin"), F.col("price_usd")).filter(F.col("price_usd")>1000).show(10)

# -------------------------------------------------------------------
# BLOCK 3 — Proving lazy evaluation
# -------------------------------------------------------------------
#
# Watch this carefully — it's the concept that separates Spark from Pandas.


# Ex 7. Build a chain WITHOUT calling .show() at the end.
#       Assign it to a variable. Then print the variable directly
#       (just `print(my_var)`), NOT my_var.show().
#       What does it print? Why?
# Your code:

var = df.select(F.col("coin"), F.col("price_usd")).filter(F.col("price_usd")>1000)
print(var)

# Ex 8. Now call .show() on the same chain. What's different?
# Your code:

var.show(10)
# -------------------------------------------------------------------
# CLEAN UP
# -------------------------------------------------------------------
# Stops the SparkSession and releases resources.
spark.stop()
