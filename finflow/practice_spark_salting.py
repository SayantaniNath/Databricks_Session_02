"""
Session: Spark UI hands-on + Salting
Date: 2026-06-08

PART A — Run this FIRST. It intentionally creates skew.
         While it runs (or just after), open: http://localhost:4040
         Walk through the Spark UI to see the hot partition.

PART B — Exercises (from blank — no peeking at the walkthrough doc).
         Write the salting fix for both scenarios below.

Data:
  transactions_skewed.jsonl  — 50,000 rows, 80% merchant_id = MEGACORP
  merchants.jsonl            — 5 merchant rows (small lookup table)
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (SparkSession.builder
         .appName("salting_exercise")
         .config("spark.sql.shuffle.partitions", "10")   # low so skew is obvious in UI
         .config("spark.sql.adaptive.enabled", "false")  # AQE OFF so Spark can't auto-fix skew
         .config("spark.sql.autoBroadcastJoinThreshold", "-1")  # force SMJ — merchants won't be
                                                                 # auto-broadcast; both tables shuffle
                                                                 # on merchant_id → MEGACORP's 40K rows
                                                                 # land in 1 partition → skew visible
         .getOrCreate())

spark.sparkContext.setLogLevel("ERROR")

DATA = "data/raw/transactions_skewed.jsonl"
META = "data/raw/merchants.jsonl"

txns = spark.read.json(DATA)
merchants = spark.read.json(META)

print(f"\nTotal transactions: {txns.count()}")
print("\nDistribution by merchant_id (shows the skew):")
txns.groupBy("merchant_id").count().orderBy(F.desc("count")).show()

# ─────────────────────────────────────────────────
# PART A — SKEWED JOB (intentional, no fix applied)
# Open http://localhost:4040 WHILE this runs or right after
# ─────────────────────────────────────────────────

print("\n--- PART A: Running SKEWED join (AQE off, no salting) ---")
print("Open http://localhost:4040 now to watch the stages\n")

skewed_result = (
    txns.join(merchants, on="merchant_id", how="inner")
        .groupBy("merchant_id", "category")
        .agg(
            F.count("*").alias("txn_count"),
            F.sum("amount").alias("total_amount"),
            F.avg("amount").alias("avg_amount"),
        )
        .orderBy(F.desc("txn_count"))
)
skewed_result.show()

print("\n>>> Spark UI checklist (look at the slow stage):")
print("    Stages tab → click the slowest stage")
print("    Summary Metrics → look at 'Shuffle Read Size'")
print("    Check: Min vs Median vs Max — large Max/Median ratio = skew")
print("    Tasks tab → sort by Duration — one task should be much longer")
print()
input(">>> UI is live at http://localhost:4040 — browse it now, press Enter when done...")

# ─────────────────────────────────────────────────
# PART B — EXERCISES (write from blank below)
# ─────────────────────────────────────────────────

# ── Exercise 1: Detect skew programmatically ──────────────────────────────
# Using spark_partition_id(), show how many rows are in each partition
# after a repartition on merchant_id (10 partitions).
# Expected: one partition will have ~40,000 rows, others ~2,500 or less.
#
# YOUR CODE HERE

spark_partition_counts = (
    txns.repartition(10, "merchant_id")  # shuffle on merchant_id into 10 partitions
        .withColumn("partition_id", F.spark_partition_id())  # add partition ID column
        .groupBy("partition_id")  # group by partition ID
        .count()  # count rows per partition
        .orderBy(F.desc("count"))  # order by count desc to see skew
)

# ── Exercise 2: Join salting (large + small table) ────────────────────────
# Fix the skewed join in PART A using salting.
# txns is the large skewed table. merchants is the small lookup table.
# Use SALT_BUCKETS = 10.
#
# Steps:
#   1. Add a salt column (random int 0–9) to txns
#   2. Build the salted_key for txns: merchant_id + "_" + salt
#   3. Explode merchants to all salt values, build matching salted_key
#   4. Join on salted_key
#   5. groupBy merchant_id + category, agg count + sum + avg
#   6. Show result — should match PART A output exactly
#   7. Drop the extra columns (salt, salt_array, salted_key)
#
# YOUR CODE HERE:
SALT_BUCKETS = 10

txns_salted = (
    txns.withColumn("salt", (F.rand() * SALT_BUCKETS).cast("int")).withColumn("salted_key", F.concat_ws("_", F.col("merchant_id"), F.col("salt"))))

merchants_salted = (merchants
    .withColumn("salt_array", F.array([F.lit(i) for i in range(SALT_BUCKETS)]))
    .withColumn("salted_key", F.explode(F.col("salt_array")))
    .withColumn("salted_key", F.concat_ws("_", F.col("merchant_id"), F.col("salted_key"))))
print(f"Salted result count: {merchants_salted.count()}")

salted_result = (txns_salted
    .join(merchants_salted.drop("merchant_id"), on="salted_key", how="inner")
    .groupBy("merchant_id", "category")
    .agg(F.count("*").alias("txn_count"), F.sum("amount").alias("total_amount"), F.avg("amount").alias("avg_amount"))
    .orderBy(F.desc("txn_count"))
    .show())

input(">>> Salted job done — check http://localhost:4040, press Enter to continue...")
# ── Exercise 3: groupBy salting (aggregation only, no join) ───────────────
# Without joining merchants, compute total_amount per merchant_id
# using two-pass groupBy salting.
#
# Steps:
#   1. Add salt column (rand int 0–9)
#   2. Build salted_key: merchant_id + "_" + salt
#   3. First pass: groupBy salted_key → partial sum of amount
#   4. Strip salt from salted_key to get merchant_id back
#   5. Second pass: groupBy merchant_id → sum of partial sums
#   6. Show result, orderBy desc
#
# YOUR CODE HERE:


# ── Exercise 4: Size the salt bucket correctly ────────────────────────────
# The Spark UI (or programmatic check from Ex 1) shows:
#   Max partition rows  = 40,200
#   Median partition rows = 2,500
#   Target partition rows = 5,000
#
# Print: the skew ratio, and the correct SALT_BUCKETS value.
#
# YOUR CODE HERE:


print("\nDone. Open http://localhost:4040 → compare the salted job stages vs Part A.")
spark.stop()
