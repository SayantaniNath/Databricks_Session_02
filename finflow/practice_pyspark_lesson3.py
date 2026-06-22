"""
Stage 2B Lesson 3 — PySpark SQL: temp views + spark.sql()

Same operations you already know from the DataFrame API (Lessons 1-2),
but written as SQL strings. The whole point of this lesson: SQL and the
DataFrame API are TWO FRONT-ENDS to the SAME engine. Same Catalyst
optimizer, same physical plan, same Spark UI jobs. Pick whichever reads
better for the problem — interviews expect you to be fluent in both and
to know they're equivalent.

Write from blank. For each exercise, write the SQL version, then (where
asked) write the DataFrame-API version too and confirm they print the
SAME rows. That equivalence is the lesson.

Data: ~/Downloads/finflow/data/raw/crypto/sample.jsonl
        columns: coin, symbol, price_usd, fetched_at
      ~/Downloads/finflow/data/raw/crypto/coin_meta.jsonl
        columns: coin, full_name, consensus

Run with:  ~/myenv/bin/python ~/Downloads/finflow/practice_pyspark_lesson3.py
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pathlib import Path

spark = (
    SparkSession.builder
    .appName("FinFlow_Lesson3_SQL")
    .getOrCreate()
)

DATA = str(Path.home() / "Downloads" / "finflow" / "data" / "raw" / "crypto" / "sample.jsonl")
META = str(Path.home() / "Downloads" / "finflow" / "data" / "raw" / "crypto" / "coin_meta.jsonl")

df = spark.read.json(DATA)
meta = spark.read.json(META)


# ===================================================================
# BLOCK 0 — register the DataFrames as SQL tables (views)
# ===================================================================
#
# Before you can run SQL against a DataFrame, you give it a NAME that
# the SQL engine can see:
#
#   df.createOrReplaceTempView("prices")
#
#   - "prices" is now a queryable table name, scoped to this SparkSession.
#   - "OrReplace" = re-running the script won't error on "view exists".
#   - It's just a label on the existing df — NO data is copied or computed.
#   - Then you run:  spark.sql("SELECT ... FROM prices")
#     which returns a NEW DataFrame (lazy — needs .show()/an action to run).
#
# Register both frames so the join exercises have two tables to work with.

df.createOrReplaceTempView("prices")
meta.createOrReplaceTempView("coin_meta")


# ===================================================================
# BLOCK 1 — SELECT / WHERE  (mirrors select + filter)
# ===================================================================
#
# DataFrame API:  df.select("coin", "price_usd").filter(F.col("price_usd") > 1000)
# SQL          :  spark.sql("SELECT coin, price_usd FROM prices WHERE price_usd > 1000")
#
# spark.sql(...) returns a DataFrame, so you still call .show() on it.


# Ex 1. Using SQL, select coin + price_usd from `prices` where price_usd > 1000.
#       Show it.
# Your code:

spark.sql("SELECT coin, price_usd FROM prices where price_usd>1000").show(10)



# Ex 2. Write the SAME query using the DataFrame API (select + filter).
#       Show it. Confirm the rows match Ex 1.
# Your code:

df.select("coin", "price_usd").filter(F.col("price_usd") >1000).show(10)


# ===================================================================
# BLOCK 2 — derived columns  (mirrors withColumn)
# ===================================================================
#
# SQL does derived columns inline in the SELECT list with AS:
#
#   SELECT coin,
#          price_usd,
#          ROUND(price_usd * 83, 2) AS price_inr
#   FROM prices
#
# AS gives the computed column a name — the SQL equivalent of .alias().


# Ex 3. SQL: select coin, price_usd, and price_usd * 83 rounded to 2 decimals
#       aliased as price_inr. Show it.
# Your code:

spark.sql("select coin, price_usd, ROUND(price_usd * 0.93, 2) as price_inr from prices").show(10)



# ===================================================================
# BLOCK 3 — GROUP BY + aggregates  (mirrors groupBy + agg)
# ===================================================================
#
#   SELECT coin,
#          AVG(price_usd) AS avg_price,
#          MAX(price_usd) AS max_price,
#          COUNT(*)       AS n
#   FROM prices
#   GROUP BY coin
#
# Rule that trips people up: every column in SELECT must either be in the
# GROUP BY or wrapped in an aggregate function. Same shuffle as .groupBy().


# Ex 4. SQL: per coin, get avg price (avg_price), max price (max_price),
#       and row count (n). Group by coin. Show it.
# Your code:


spark.sql("SELECT coin, AVG(price_usd) AS avg_price, MAX(price_usd) AS max_price, COUNT(*) AS n FROM prices GROUP BY coin").show(10)

# Ex 5. Write the SAME aggregation with the DataFrame API
#       (groupBy().agg(...)). Show it. Confirm it matches Ex 4.
# Your code:

df.groupBy("coin").agg(F.avg("price_usd"), F.max("price_usd"), F.count("*").alias("count of all records")).show(10)



# ===================================================================
# BLOCK 4 — ORDER BY  (mirrors orderBy)
# ===================================================================
#
#   SELECT coin, AVG(price_usd) AS avg_price
#   FROM prices
#   GROUP BY coin
#   ORDER BY avg_price DESC
#
# ORDER BY runs AFTER GROUP BY, so it can sort by the aggregate alias.


# Ex 6. SQL: avg price per coin, ordered by avg_price DESCENDING. Show it.
# Your code:

spark.sql("SELECT coin, AVG(price_usd) AS avg_price FROM prices GROUP BY coin ORDER BY avg_price DESC").show(10)


df.groupBy("coin").agg(F.avg("price_usd").alias("avg_price")).orderBy(F.col("avg_price").desc()).show(10)

# ===================================================================
# BLOCK 5 — JOIN  (mirrors df.join)
# ===================================================================
#
#   SELECT p.coin, p.price_usd, m.full_name, m.consensus
#   FROM prices p
#   JOIN coin_meta m  ON p.coin = m.coin
#
#   - Table aliases (p, m) keep column refs unambiguous.
#   - JOIN with no qualifier = INNER JOIN.
#   - LEFT JOIN keeps all `prices` rows even with no metadata match.


# Ex 7. SQL: inner-join prices + coin_meta on coin. Select
#       coin, price_usd, full_name, consensus. Show it.
# Your code:

spark.sql("SELECT p.coin, p.price_usd, m.full_name, m.consensus FROM prices p JOIN coin_meta m ON p.coin = m.coin").show(10)

df.join(meta, on = "coin", how = 'inner').select(F.col("coin"), F.col("price_usd"), F.col("full_name"), F.col("consensus")).show(10)

# Ex 8. SQL: join, then GROUP BY consensus and get avg price_usd per
#       consensus type (avg_price). One query. Show it.
#       (This is Ex 11 from Lesson 2 — now in SQL.)
# Your code:

spark.sql("SELECT m.consensus, AVG(p.price_usd) AS avg_price FROM prices p JOIN coin_meta m ON p.coin = m.coin GROUP BY m.consensus").show(10)

df.join(meta, on = "coin", how = "inner").groupBy("consensus").agg(F.avg("price_usd").alias("avg_price")).show(10)

# Ex 9. Write Ex 8 with the DataFrame API (join → groupBy → agg).
#       Show it. Confirm it matches Ex 8.
# Your code:




# ===================================================================
# BLOCK 6 — same plan, proof  (explain on a SQL query)
# ===================================================================
#
# The payoff: a SQL query and its DataFrame-API twin compile to the
# SAME physical plan. Call .explain() on both and compare.


# Ex 10. Call .explain() on your Ex 8 SQL query (the join+groupBy), and
#        .explain() on your Ex 9 DataFrame version. Eyeball the physical
#        plan at the bottom of each — they should be effectively identical
#        (same BroadcastHashJoin, same Exchange/HashAggregate).
# Your code:

spark.sql("SELECT m.consensus, AVG(p.price_usd) AS avg_price FROM prices p JOIN coin_meta m ON p.coin = m.coin GROUP BY m.consensus").explain(True)

df.join(meta, on = "coin", how = "inner").groupBy("consensus").agg(F.avg("price_usd").alias("avg_price")).explain(True)

# ===================================================================
# WRAP — keep the Spark UI alive so you can confirm in the browser
# ===================================================================
# Open http://localhost:4040 while this is paused:
#   - SQL tab: your spark.sql() queries appear here just like DataFrame
#     ones. Click one → same DAG, same BroadcastHashJoin you saw last time.
#   - That's the whole lesson made visual: SQL front-end, same engine.

import time
print("\n>>> Spark UI live at http://localhost:4040 — staying up for 5 minutes...\n", flush=True)
time.sleep(300)

spark.stop()
