"""
Stage 2B Lesson 2 — DataFrame API: withColumn, groupBy/agg, orderBy, join
                     + LIVE Spark UI walkthrough (closes yesterday's loop)

Write from blank. Lesson 1 already covered show / printSchema / count /
select / filter / lazy evaluation — this file picks up from there.

Data: ~/Downloads/finflow/data/raw/crypto/sample.jsonl
Columns: coin, symbol, price_usd, fetched_at

Run with:  ~/myenv/bin/python ~/Downloads/finflow/practice_pyspark_lesson2.py
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pathlib import Path

spark = (
    SparkSession.builder
    .appName("FinFlow_Lesson2")
    .getOrCreate()
)

DATA = str(Path.home() / "Downloads" / "finflow" / "data" / "raw" / "crypto" / "sample.jsonl")
df = spark.read.json(DATA)


# ===================================================================
# BLOCK 1 — withColumn  (add / replace a derived column)
# ===================================================================
#
# Pandas:  df["price_inr"] = df["price_usd"] * 83
# Spark :  df.withColumn("price_inr", F.col("price_usd") * 83)
#
#   df.withColumn("newname", <expression>)   → returns a NEW df with the column added
#   If "newname" already exists, it REPLACES that column.
#   It's a transformation — nothing runs until an action.
#
# Useful expression helpers:
#   F.col("c")            → reference a column
#   F.round(expr, 2)      → round to 2 decimals
#   F.upper(F.col("c"))   → uppercase a string column
#   F.lit(83)             → a literal/constant value (needed for some ops)


# Ex 1. Add a column `price_inr` = price_usd * 83. Show coin + price_usd + price_inr.
# Your code:

df.withColumn("price_inr", F.col("price_usd") * 83).select (F.col("coin"), F.col("price_usd"), F.col("price_inr")).show(10)


# Ex 2. Add a column `symbol_upper` = uppercase of symbol. Show symbol + symbol_upper.
# Your code:

df.withColumn("symbol_upper", F.upper(F.col("symbol"))).select(F.col("symbol"), F.col("symbol_upper")).show(10)


# Ex 3. Add `price_inr_rounded` = price_usd * 83 rounded to 2 decimals. Show it.
# Your code:

df.withColumn("price_inr_rounded", F.round(F.col("price_usd") * 83, 2)).select(F.col("coin"), F.col("price_usd"), F.col("price_inr_rounded")).show(10)
# ===================================================================
# BLOCK 2 — groupBy + agg  (the most-tested DE operation)
# ===================================================================
#
# Pandas:  df.groupby("coin")["price_usd"].mean()
# Spark :  df.groupBy("coin").agg(F.avg("price_usd"))
#
#   df.groupBy("col")                       → returns a GroupedData object
#   .agg(F.avg("price_usd"))                → one aggregation
#   .agg(F.avg("price_usd"), F.max("price_usd"))   → multiple aggregations
#   .agg(F.avg("price_usd").alias("avg_price"))    → rename the output column
#
# Common agg functions: F.avg, F.sum, F.min, F.max, F.count, F.countDistinct
#
# NOTE: groupBy triggers a SHUFFLE (wide transformation). Watch for this
#       in the Spark UI later — it creates a stage boundary.


# Ex 4. Group by coin, get the AVG price_usd per coin. Show it.
# Your code:

df.groupBy("coin").agg(F.avg("price_usd").alias("avg_price")).show(10)

# Ex 5. Group by coin, get avg price AND max price in one .agg(),
#       aliasing them "avg_price" and "max_price". Show it.
# Your code:

df.groupBy("coin").agg(F.avg("price_usd").alias("avg_price"), F.max("price_usd").alias("max_price")).show(10)

# Ex 6. Count how many rows exist per coin (groupBy + F.count). Show it.
#       Hint: F.count("*") or F.count(F.lit(1)) both work.
# Your code:

df.groupBy("coin").agg(F.count("*").alias("count")).show(10)
# ===================================================================
# BLOCK 3 — orderBy / sort  (also a shuffle)
# ===================================================================
#
#   df.orderBy("price_usd")                       → ascending
#   df.orderBy(F.col("price_usd").desc())         → descending
#   df.orderBy(F.desc("price_usd"))               → same, function form
#   .sort(...) is an alias for .orderBy(...)
#
# orderBy is a WIDE transformation — another shuffle / stage boundary.


# Ex 7. Show all rows sorted by price_usd DESCENDING (highest first).
# Your code:
df.orderBy(F.col("price_usd").desc()).show(10)

# Ex 8. Chain it: avg price per coin (Block 2), then order by avg_price DESC.
#       One chained statement. Show the result.
# Your code:
df.groupBy("coin").agg(F.avg("price_usd").alias("avg_price")).orderBy(F.col("avg_price").desc()).show(10)

# ===================================================================
# BLOCK 4 — join  (combine two DataFrames)
# ===================================================================
#
# A small second DataFrame = coin metadata. In real pipelines this is
# another table/file, so we read it from a JSON file (same as df above).
# NOTE: we read from a file instead of spark.createDataFrame([...]) because
# this venv's Python 3.14 + PySpark 3.5.8 can't serialize Python lists into
# Spark (a known version mismatch). Reading files avoids that broken path.

META = str(Path.home() / "Downloads" / "finflow" / "data" / "raw" / "crypto" / "coin_meta.jsonl")
meta = spark.read.json(META)

#   df.join(other, on="coin", how="inner")   → matched rows only
#   how options: "inner" (default), "left", "right", "outer"
#   on="coin" works because BOTH frames have a column named coin.
#
# Small-table joins like this become a BROADCAST join — Spark ships the
# tiny `meta` frame to every executor instead of shuffling. You'll see
# "BroadcastHashJoin" in the Spark UI / explain plan.


# Ex 9. Inner-join df with meta on "coin". Show coin + price_usd + full_name + consensus.
# Your code:

df.join(meta, on = "coin", how = "inner").select(F.col("coin"), F.col("price_usd"), F.col("full_name"), F.col("consensus")).show(10)


# Ex 10. LEFT join df with meta on "coin". (Same result here since all coins
#        have metadata — but say WHEN left vs inner would differ.)
# Your code:

df.join(meta, on = "coin", how = "left").select(F.col("coin"), F.col("price_usd"), F.col("full_name"), F.col("consensus")).show(10)


# Ex 11. After the inner join, group by `consensus` and get avg price_usd
#        per consensus type. Show it. (join → groupBy → agg, chained.)
# Your code:

df.join(meta, on = "coin", how = "inner").groupBy("consensus").agg(F.avg("price_usd").alias("avg_price")).show(10)

# ===================================================================
# BLOCK 5 — explain()  (see the optimized plan BEFORE running)
# ===================================================================
#
#   any_df.explain()        → prints the physical plan
#   any_df.explain(True)    → prints parsed / analyzed / optimized / physical
#
# Look for: PushedFilters, BroadcastHashJoin, Exchange (= a shuffle).


# Ex 12. Take your Ex 11 chain (join → groupBy → agg) and call .explain()
#        on it instead of .show(). Find the word "Exchange" (shuffle) and
#        "BroadcastHashJoin" in the output.
# Your code:

df.join(meta, on = "coin", how = "inner").groupBy("consensus").agg(F.avg("price_usd").alias("avg_price")).explain(True)


# ===================================================================
# SPARK UI — LIVE (this closes yesterday's missing piece)
# ===================================================================
# While this script is paused below, the Spark UI is live at:
#
#       http://localhost:4040
#
# Before you hit Enter to quit, open that URL and look at:
#   - Jobs tab     → one job per ACTION you ran (each .show()/.count())
#   - Stages tab   → click a job; count the stages. groupBy/orderBy/join
#                    each add a stage boundary (shuffle = "Exchange").
#   - SQL tab      → click a query → see the DAG diagram + BroadcastHashJoin
#   - Tasks        → inside a stage, see tasks = partitions processed
#
# Self-check questions while you browse:
#   1. How many Jobs are listed? (should ≈ number of actions you ran)
#   2. Pick the Ex 11 query in the SQL tab — how many Exchanges (shuffles)?
#   3. Is the join shown as BroadcastHashJoin or SortMergeJoin? Why?

import time
print("\n>>> Spark UI live at http://localhost:4040 — staying up for 10 minutes...\n", flush=True)
time.sleep(600)   # keep the SparkSession (and the UI) alive while you browse

spark.stop()
