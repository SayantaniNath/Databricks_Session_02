"""
Pandas Lesson 3 — Summary Functions and Maps
Practice file (write from blank — no peeking at Lesson 2).

Data: ~/Downloads/finflow/data/raw/crypto/sample.jsonl
Columns: coin, symbol, price_usd, fetched_at

"/Users/sayantaninath/Downloads/finflow/data/raw/crypto/sample.jsonl"
"""

import pandas as pd
from pathlib import Path

DATA = Path.home() / "Downloads" / "finflow" / "data" / "raw" / "crypto" / "sample.jsonl"
df = pd.read_json(DATA, lines=True)

print("--- df ---")
print(df)
print()

# -------------------------------------------------------------------
# BLOCK 1 — Summary functions
# -------------------------------------------------------------------

# Ex 1. Print the mean and the median of price_usd.
#       Are they close, or far apart? What does that tell you about the
#       price distribution across these coins?
#
# Your code:
print("Mean of price usd ", df["price_usd"].mean())


# Ex 2. How many unique coin symbols are in the file?
#       (One function gives you the array of unique values;
#        len() on that gives the count.)
#
# Your code:

print("Unique symbols count ", len(df["symbol"].unique()))


# Ex 3. Call describe() on price_usd. Look at the output.
#       Which is bigger — the mean or the median? What does the gap
#       between min and max tell you?
#
# Your code:

print ("Describe price_usd ", df["price_usd"].describe())


# -------------------------------------------------------------------
# BLOCK 2 — Maps (map and apply)
# -------------------------------------------------------------------
#
# Quick reference:
#   .map(func)   — runs on a Series only. Applies func to every value.
#                  Returns a new Series. Original is unchanged.
#   .apply(func) — runs on a Series OR a DataFrame.
#                  On a DataFrame with axis=1, func gets one ROW at a time.
#                  On a DataFrame with axis=0 (default), func gets one COLUMN.
#
# A "lambda" is a tiny one-line anonymous function:
#     lambda x: x * 0.92    is equivalent to    def f(x): return x * 0.92


# Ex 4 (map). Build a new column `price_eur` = price_usd converted to EUR
#             at a fixed rate of 0.92 EUR per USD.
#             Use .map() with a lambda.
#             Then print df to see the new column.
#
# Your code:

print("Before mapp", df)
df["price_eur"] = df["price_usd"].map(lambda x :x*0.92)
print("After map", df)

# Ex 5 (apply on a Series). Build a new column `tier` that contains
#             "high" if price_usd > 1000, otherwise "low".
#             Use .apply() with a lambda (conditional expression).
#             Then print df.
#
# Your code:
df["tier"] = df["price_usd"].apply(lambda x : "high" if x>1000 else "low")
print(df)

# Ex 6 (apply on a DataFrame, axis=1). Build a new column `label` that
#             reads like "bitcoin: $67123.45" — i.e. f-string combining
#             the row's coin and price_usd.
#             Use .apply() with axis=1 and a lambda that takes one row.
#             Then print df.
#
# Your code:
df["label"] = df.apply(lambda row : f"{row['coin']}: ${row['price_usd']:.2f}", axis = 1)
print(df)


# -------------------------------------------------------------------
# BLOCK 3 — idxmax / idxmin (find the row of the extremum)
# -------------------------------------------------------------------
#
# .max() / .min()   — give you the max/min VALUE in a Series.
# .idxmax() / .idxmin() — give you the INDEX (row label) where that
#                         max/min occurs.
#
# Why it matters: tells you WHERE the extreme is, not just what it is.
# Common interview pattern: "which user/product/etc had the highest X?"


# Ex 7. Find the row index of the most expensive coin observation,
#       then use .loc to print the whole row.
#
# Hints:
#   max_idx = df["price_usd"].idxmax()
#   print(df.loc[max_idx])
#
# Your code:

print(df.loc[df["price_usd"].idxmax()])



# -------------------------------------------------------------------
# BLOCK 4 — Vectorized math (Pandas does the loop for you)
# -------------------------------------------------------------------
#
# You can do math on a whole Series with one expression.
# Pandas applies it element-wise — no lambda, no loop.
#
# Examples:
#   df["price_usd"] * 0.92               # same as Ex 4 but no lambda
#   df["price_usd"] - df["price_usd"].mean()   # re-center around 0
#   df["price_usd"] / df["price_usd"].max()    # normalize to 0..1
#
# These are FASTER than .map() / .apply() because they run in C under
# the hood. Rule of thumb: if you can do it with a built-in operator,
# skip the lambda.


# Ex 8. Build a new column `price_centered` = price_usd minus the mean
#       of price_usd. (No .map, no .apply. Just one line of math.)
#       Then print df. Notice — the column will have positive values for
#       above-average prices and negative for below-average.
#
# Your code:

df["price_centered"] = df["price_usd"] - df["price_usd"].mean()
print (df)
