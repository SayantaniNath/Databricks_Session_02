"""
Pandas Lesson 2 — Indexing, Selecting & Assigning (from-blank practice)
-----------------------------------------------------------------------

Goal: practice iloc, loc, boolean indexing, and assigning data — from scratch,
no peeking at the chat. Struggle 2-3 min per problem before checking.

DATA SHAPE (memorize):
       coin symbol  price_usd                fetched_at
    0   bitcoin    btc   67123.45 2026-05-15 10:00:00+00:00
    1  ethereum    eth    3210.10 2026-05-15 10:00:00+00:00
    2    solana    sol     148.77 2026-05-15 10:00:00+00:00
    3   bitcoin    btc   67890.12 2026-05-16 10:00:00+00:00
    4  ethereum    eth    3155.40 2026-05-16 10:00:00+00:00
    5    solana    sol     151.20 2026-05-16 10:00:00+00:00

RUN WITH:
    ~/myenv/bin/python ~/Downloads/finflow/practice_pandas_lesson2.py
"""

import pandas as pd

path = "/Users/sayantaninath/Downloads/finflow/data/raw/crypto/sample.jsonl"


# ---------------------------------------------------------------
# Exercise 1 — Load the data
# ---------------------------------------------------------------
# Read the JSONL file into a DataFrame called `df`.
# Hint: it's the same one-liner you wrote yesterday in practice_pandas_02.py.

df = pd.read_json(path, lines = True)   # TODO

print("Exercise 1 — loaded DataFrame:")
print(df)
print()


# ---------------------------------------------------------------
# Exercise 2 — Boolean filter
# ---------------------------------------------------------------
# Filter `df` to only the rows where price_usd is greater than 50000.
# Save the result as `expensive`.

expensive = df.loc[df["price_usd"]>50000]  # TODO

print("Exercise 2 — expensive rows (price_usd > 50000):")
print(expensive)
print()


# ---------------------------------------------------------------
# Exercise 3 — .loc with a condition + column list
# ---------------------------------------------------------------
# Using .loc, get the `symbol` and `fetched_at` columns ONLY for the
# expensive rows (same filter as Exercise 2). Save as `expensive_slim`.
#
# Hint: .loc[row_filter, [list, of, columns]]

expensive_slim = df.loc[df["price_usd"]>50000, ["symbol", "fetched_at"]]   # TODO

print("Exercise 3 — expensive rows, only symbol + fetched_at:")
print(expensive_slim)
print()


# ---------------------------------------------------------------
# Exercise 4 — .iloc positional slice
# ---------------------------------------------------------------
# Using .iloc, grab the FIRST 3 ROWS and the LAST 2 COLUMNS of `df`.
# Save as `top_corner`.
#
# Hint 1: .iloc[rows, cols]
# Hint 2: "last 2 columns" → think negative indexing

top_corner = df.iloc[0:3, -2:]  # TODO

print("Exercise 4 — first 3 rows, last 2 columns:")
print(top_corner)
print()


# ---------------------------------------------------------------
# Exercise 5 — Add a computed column
# ---------------------------------------------------------------
# Add a new column called `price_eur` to `df`, computed as
# price_usd * 0.92.

# TODO: add the column here
df["price_eur"] = df["price_usd"] * 0.92

print("Exercise 5 — df with price_eur column:")
print(df)
