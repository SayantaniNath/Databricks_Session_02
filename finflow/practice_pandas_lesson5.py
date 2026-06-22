"""
Pandas Lesson 5 — Data Types and Missing Values
Practice file (write from blank — no peeking at Lesson 4).

Data: ~/Downloads/finflow/data/raw/crypto/sample.jsonl
Columns: coin, symbol, price_usd, fetched_at
"""

import numpy as np
import pandas as pd
from pathlib import Path

DATA = Path.home() / "Downloads" / "finflow" / "data" / "raw" / "crypto" / "sample.jsonl"
df = pd.read_json(DATA, lines=True)

print("--- df ---")
print(df)
print()


# -------------------------------------------------------------------
# BLOCK 1 — dtypes
# -------------------------------------------------------------------
#
# Every column has a type. Pandas infers it on read, but the inference
# isn't always what you want.
#
# Common dtypes:
#   int64           → whole numbers
#   float64         → decimals (also: any column with NaN, even ints)
#   object          → strings, or mixed types
#   bool            → True/False
#   datetime64[ns]  → real timestamps (NOT the same as a date-shaped string)
#
# Two forms:
#   df.dtypes        → Series: column name → dtype (whole DataFrame)
#   df["col"].dtype  → single dtype (note: singular, on a Series)
#
# Gotcha: one NaN in an int column makes the whole column float64.
# There is no integer-NaN in classic pandas.


# Ex 1. Print the dtype of every column.
# Your code:

print(df.dtypes)

# Ex 2. Print just the dtype of `price_usd`.
# Your code:

print(df["price_usd"].dtype)

# Ex 3. Look at the output of Ex 1. Is `fetched_at` a real datetime,
#       or an object (string)? Write the answer as a comment.
# Your answer:

# 'fetched_at' is datetime64[ns]
# -------------------------------------------------------------------
# BLOCK 2 — astype: converting dtypes
# -------------------------------------------------------------------
#
# .astype(<dtype>) returns a NEW Series with the converted type.
# Common targets:
#   .astype("int64")
#   .astype("float64")
#   .astype("string")          → pandas StringDtype (preferred for text)
#   pd.to_datetime(series)     → convert a string column to datetime64
#
# Note: pd.to_datetime() is the idiomatic way to parse dates — astype
# CAN do it but to_datetime is more forgiving with formats.


# Ex 4. Convert `fetched_at` from object → datetime64.
#       Assign back to df["fetched_at"]. Then print df.dtypes again
#       and confirm it changed.
# Your code:

df["fetched_at"] = pd.to_datetime(df["fetched_at"])

# Ex 5. Make a new column `price_int` that is `price_usd` cast to int.
#       (Truncates the decimals.)
# Your code:

df["price_int"] = df["price_usd"].astype("int64")


# -------------------------------------------------------------------
# BLOCK 3 — Missing values: detection
# -------------------------------------------------------------------
#
# NaN ("Not a Number") = pandas' marker for missing. It's a float.
# You compare for it with isnull() / notnull(), NOT with == NaN.
#
#   df.isnull()           → DataFrame of True/False, same shape as df
#   df["col"].isnull()    → Series of True/False
#   df.isnull().sum()     → count of missing per column (super useful)
#   df.notnull()          → the inverse
#
# Our sample data has no NaNs, so we'll inject some first.


# Inject NaN into `price_usd` at rows 0 and 2, just for practice:
df.loc[[0, 2], "price_usd"] = np.nan
print("--- df with injected NaN ---")
print(df)
print()


# Ex 6. Print a boolean Series showing which rows have a missing
#       `price_usd`.
# Your code:

print(df["price_usd"].isnull())

# Ex 7. Print the COUNT of missing values per column (one number per column).
# Your code:

print(df.isnull().sum())

# Ex 8. Print only the rows where `price_usd` is missing.
#       (Hint: boolean indexing with .isnull())
# Your code:

print(df[df["price_usd"].isnull()])

# -------------------------------------------------------------------
# BLOCK 4 — fillna: replace missing values
# -------------------------------------------------------------------
#
# .fillna(value) returns a NEW Series/DataFrame with NaN replaced.
# Common patterns:
#   df["col"].fillna(0)                  → fill with a constant
#   df["col"].fillna(df["col"].mean())   → fill with the column's mean
#   df["col"].ffill()                    → forward-fill (use previous value)
#   df["col"].bfill()                    → back-fill (use next value)


# Ex 9. Fill missing `price_usd` with 0. Print the result.
#       (Don't reassign — just print it.)
# Your code:

print(df["price_usd"].fillna(0))

# Ex 10. Fill missing `price_usd` with the MEAN of the non-missing prices.
#        Print the result.
# Your code:

print(df["price_usd"].fillna(df["price_usd"].mean()))

# -------------------------------------------------------------------
# BLOCK 5 — dropna: remove missing
# -------------------------------------------------------------------
#
# .dropna() returns a new DataFrame with rows containing any NaN removed.
# Variants:
#   df.dropna()                 → drop rows with any NaN
#   df.dropna(subset=["col"])   → drop only if `col` is NaN
#   df.dropna(axis=1)           → drop COLUMNS that have any NaN


# Ex 11. Drop the rows where `price_usd` is missing. Print the result.
# Your code:

print(df.dropna(subset=["price_usd"]))

# -------------------------------------------------------------------
# BLOCK 6 — replace: swap specific values
# -------------------------------------------------------------------
#
# .replace(old, new) swaps specific values. Different from fillna —
# fillna only targets NaN; replace targets any specific value.
#
#   df["col"].replace("btc", "BTC")
#   df["col"].replace({"btc": "BTC", "eth": "ETH"})   → dict form


# Ex 12. Replace "btc" with "BTC" in the `symbol` column. Print the result.
# Your code:

print(df["symbol"].replace("btc", "BTC"))

# Ex 13. Using the dict form, uppercase ALL symbols
#        (btc→BTC, eth→ETH, ada→ADA, sol→SOL, etc — match what's in your data).
# Your code:

print(df["symbol"].replace({"btc": "BTC", "eth": "ETH", "sol": "SOL"}))
