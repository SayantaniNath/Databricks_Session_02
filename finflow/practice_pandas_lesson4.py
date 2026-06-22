"""
Pandas Lesson 4 — Grouping and Sorting
Practice file (write from blank — no peeking at Lesson 3).

Data: ~/Downloads/finflow/data/raw/crypto/sample.jsonl
Columns: coin, symbol, price_usd, fetched_at
"""

import pandas as pd
from pathlib import Path

DATA = Path.home() / "Downloads" / "finflow" / "data" / "raw" / "crypto" / "sample.jsonl"
df = pd.read_json(DATA, lines=True)

print("--- df ---")
print(df)
print()

# -------------------------------------------------------------------
# BLOCK 1 — groupby + a single aggregation
# -------------------------------------------------------------------
#
# .groupby("col") splits the DataFrame into mini-DataFrames, one per
# unique value of "col". Then you call an aggregation function — that
# function runs once per group, returning one row per group.
#
# Mental model:
#   df.groupby("symbol")["price_usd"].mean()
#   = "for each symbol, give me the mean of price_usd"
#
# Returns a Series indexed by the group key (symbol).


# Ex 1. For each coin symbol, print the MEAN price.
#       (Use df.groupby("symbol")["price_usd"].mean())
#
# Your code:

print(df.groupby("symbol")["price_usd"].mean())


# Ex 2. For each coin symbol, print HOW MANY rows there are.
#       (Hint: .count() on the grouped Series)
#
# Your code:

print(df.groupby("symbol")["price_usd"].count())
# Ex 3. For each coin symbol, print the MAX price observed.
#
# Your code:
print(df.groupby("symbol")["price_usd"].max())

"""┌────────────────────────┬──────────────────────────────────────────────┬───────────────────────────────────────────┐
  │                        │                  .unique()                   │                .nunique()                 │
  ├────────────────────────┼──────────────────────────────────────────────┼───────────────────────────────────────────┤
  │ Returns                │ the distinct values themselves (as an array) │ the count of distinct values (an integer) │
  ├────────────────────────┼──────────────────────────────────────────────┼───────────────────────────────────────────┤
  │ For your symbol column │ array(["btc", "eth", "sol"])                 │ 3                                         │
  ├────────────────────────┼──────────────────────────────────────────────┼───────────────────────────────────────────┤
  │ When to use            │ when you need to see the values              │ when you only need how many               │
  └────────────────────────┴──────────────────────────────────────────────┴───────────────────────────────────────────┘
"""
# -------------------------------------------------------------------
# BLOCK 2 — groupby with .agg() (multiple aggregations at once)
# -------------------------------------------------------------------
#
# Calling one function at a time (.mean, .max, .count) works but is
# repetitive. .agg() lets you ask for several aggregations in one call.
#
# Single column, multiple aggs:
#   df.groupby("symbol")["price_usd"].agg(["min", "max", "mean"])
#   → DataFrame with one row per symbol, one column per agg.
#
# Multiple columns, different aggs each:
#   df.groupby("symbol").agg({"price_usd": "mean", "fetched_at": "count"})
#   → DataFrame with one row per symbol, columns per the dict.


# Ex 4. For each coin symbol, in ONE call to .agg(), get the min, max,
#       and mean of price_usd. Print the result.
#
# Your code:


# Ex 5. For each coin symbol, in ONE call to .agg() using a dict,
#       get the MEAN of price_usd AND the COUNT of fetched_at.
#       Print the result.
#
# Your code:

print(df.groupby("symbol")["price_usd"].agg(["min", "max", "count", "mean", "median", "nunique"]))

print(df.groupby("symbol").agg({"price_usd" : "mean", "fetched_at" : "count"}))


# -------------------------------------------------------------------
# BLOCK 3 — sort_values and sort_index
# -------------------------------------------------------------------
#
# .sort_values(by="col")           — sort rows by a column's values (ascending)
# .sort_values(by="col", ascending=False)   — descending order
# .sort_values(by=["col1", "col2"])         — multi-key sort
# .sort_index()                    — sort by the row labels (index) instead of values
#
# Both return a NEW DataFrame — original is unchanged.


# Ex 6. Sort the original df by price_usd, descending (highest first).
#       Print the result.
#
# Your code:
print(df.sort_values(by = "price_usd", ascending=False))


# Ex 7. From the per-symbol summary you built in Ex 5, sort by price_usd
#       descending (so the most expensive coin shows first).
#       Hint: chain .sort_values("price_usd", ascending=False) on the end.
#
# Your code:

print(df.groupby("symbol").agg({"price_usd" : "mean", "fetched_at" : "count"}).sort_values(by = "price_usd", ascending=False))

# -------------------------------------------------------------------
# BLOCK 4 — reset_index and a peek at MultiIndex
# -------------------------------------------------------------------
#
# When you groupby, the group key becomes the INDEX of the result.
# Sometimes you want it back as a regular column (e.g., for plotting,
# joining, or writing to disk). That's what .reset_index() does.
#
# Example:
#   g = df.groupby("symbol")["price_usd"].mean()   # symbol is the index
#   g.reset_index()                                # symbol becomes a column,
#                                                  # new 0..N integer index added
#
# MultiIndex (peek only — Lesson 5/6 covers this properly):
#   .groupby(["col1", "col2"])  → result has a 2-level index.
#   Treat it as one composite key for now; reset_index() flattens it.


# Ex 8. Build the same per-symbol mean-price summary, then reset_index()
#       so `symbol` is a regular column. Print it.
#
# Your code:
print(df.groupby("symbol")["price_usd"].mean().reset_index())


# Ex 9 (MultiIndex peek). Group by BOTH "symbol" AND "fetched_at" and
#       get the mean price. Print it — notice the 2-level index.
#       Then call .reset_index() on the result and print again — notice
#       the index is now flat 0,1,2,... with both keys as columns.
#
# Your code:
print(df.groupby(["symbol", "fetched_at"])["price_usd"].mean().reset_index())


""" Rule: df["new_col"] = X only works cleanly when X has the same number of rows as df, with matching index.

  Look at the shapes:

  ┌──────────────────────────────────────────┬─────────────────────────┬───────────────────────────────────────────────┐
  │             Right-hand side              │          Shape          │         Works as df["new_col"] = ...?         │
  ├──────────────────────────────────────────┼─────────────────────────┼───────────────────────────────────────────────┤
  │ df["price_usd"] * 0.92                   │ 6 rows, index 0..5      │ ✅ matches df row-for-row                     │
  ├──────────────────────────────────────────┼─────────────────────────┼───────────────────────────────────────────────┤
  │ df["price_usd"].mean()                   │ scalar (one number)     │ ✅ broadcasts — all 6 rows get the same value │
  ├──────────────────────────────────────────┼─────────────────────────┼───────────────────────────────────────────────┤
  │ df.groupby("symbol")["price_usd"].mean() │ 3 rows, index by symbol │ ❌ NaN everywhere — index mismatch            │
  └──────────────────────────────────────────┴─────────────────────────┴───────────────────────────────────────────────┘

  groupby().mean() reduces 6 rows → 3 rows. You can't paste 3 values back onto a 6-row table by position — the indexes don't line up (df is indexed 0..5; the group result is indexed by btc/eth/sol).

  So you do one of two things:
  
  1. Keep it separate — when you want a summary:
  g = df.groupby("symbol")["price_usd"].mean()
  print(g.reset_index())
  2. Put the per-group value back on every row — when you want a feature. Use .transform() instead of .mean():
  df["mean_by_symbol"] = df.groupby("symbol")["price_usd"].transform("mean")
  print(df)

  .transform() returns 6 rows (same shape as df), where each row gets the mean of its own group:

         coin symbol  price_usd            ...  mean_by_symbol
  0   bitcoin    btc   67123.45            ...      67506.785
  1  ethereum    eth    3210.10            ...       3182.750
  2    solana    sol     148.77            ...        149.985
  3   bitcoin    btc   67890.12            ...      67506.785   ← same as row 0 (both btc)
  4  ethereum    eth    3155.40            ...       3182.750
  5    solana    sol     151.20            ...        149.985

  Why it matters for DE / fraud detection — transform is the bridge from "reporting" Pandas to "feature engineering" Pandas. Classic fraud feature: transaction_amount - user_mean = z-score-ish → flag rows
   where the gap is unusually large. That entire pattern hinges on .groupby().transform().

  Mental model summary:
  - .agg() / .mean() after groupby → summary (rows shrink)
  - .transform() after groupby → feature (rows preserved)
  
  You'll re-meet this in Stage 2B with PySpark — same idea, different syntax (window functions)."""