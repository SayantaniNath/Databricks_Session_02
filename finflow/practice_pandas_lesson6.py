"""
Pandas Lesson 6 — Renaming and Combining
Practice file (write from blank — no peeking at Lesson 5).

Data: ~/Downloads/finflow/data/raw/crypto/sample.jsonl
Columns: coin, symbol, price_usd, fetched_at

This lesson uses TWO DataFrames so we can practice combining them.
The second one (df2) is created inline below — it's a small metadata table.
"""

import pandas as pd
from pathlib import Path

DATA = Path.home() / "Downloads" / "finflow" / "data" / "raw" / "crypto" / "sample.jsonl"
df = pd.read_json(DATA, lines=True)

# A second DataFrame: coin → category + launch year. We'll use this for joins.
df2 = pd.DataFrame({
    "coin":        ["bitcoin", "ethereum", "solana", "cardano"],
    "category":    ["L1",      "L1",       "L1",     "L1"],
    "launch_year": [2009,      2015,       2020,     2017],
})

print("--- df ---")
print(df)
print()
print("--- df2 ---")
print(df2)
print()


# -------------------------------------------------------------------
# BLOCK 1 — rename: change column or index labels
# -------------------------------------------------------------------
#
# .rename() returns a NEW DataFrame with renamed labels. It takes a
# dict mapping {old_name: new_name}.
#
#   df.rename(columns={"price_usd": "price"})        → rename a column
#   df.rename(index={0: "first"})                    → rename an index label
#   df.rename(columns={"a": "A", "b": "B"})          → multiple at once
#
# Key parameter: `columns=` for columns, `index=` for rows.
# Returns a NEW DataFrame — does NOT modify in place unless you use
# inplace=True (avoid that — assign back instead).


# Ex 1. Rename `price_usd` to `price` and `fetched_at` to `timestamp`.
#       Assign back to df. Print df.columns to confirm.
# Your code:

df = df.rename(columns = {"price_usd" : "price", "fetched_at" : "timestamp"})


# Ex 2. Rename the column `coin` to `name` — but ONLY for this print,
#       don't reassign df (use rename without saving the result).
# Your code:

print(df.rename(columns={"coin": "name"}))
print()
# -------------------------------------------------------------------
# BLOCK 2 — rename_axis: rename the index/columns AXIS itself
# -------------------------------------------------------------------
#
# Every DataFrame has axis names (the label ABOVE the row labels, and
# the label NEXT TO the column header row). Usually unnamed.
#
#   df.rename_axis("row_id", axis="rows")
#   df.rename_axis("fields", axis="columns")
#
# Useful when the index/columns mean something semantic
# (e.g., index = "transaction_id", columns = "metric").


# Ex 3. Rename the row axis to "row_id" and the column axis to "fields".
#       Don't reassign — just print the result.
# Your code:

print(df.rename_axis("row_id", axis="rows").rename_axis("fields", axis="columns"))

# -------------------------------------------------------------------
# BLOCK 3 — concat: stack DataFrames
# -------------------------------------------------------------------
#
# pd.concat([df_a, df_b]) glues DataFrames together.
#
#   pd.concat([a, b])               → stack VERTICALLY (rows), default
#   pd.concat([a, b], axis=1)       → stack HORIZONTALLY (columns)
#   pd.concat([a, b], ignore_index=True)  → reset the row index after stacking
#
# Used when you have the SAME columns across multiple files/sources and
# want one big DataFrame. (e.g., crypto data from two different days.)


# We'll fake "two days" by slicing df into two halves and stacking them
# back together.
df_day1 = df.iloc[:3]   # first 3 rows
df_day2 = df.iloc[3:]   # last 3 rows


# Ex 4. Stack df_day1 and df_day2 vertically with pd.concat.
#       Print the result. (Notice the index — 0,1,2,3,4,5 or 0,1,2,0,1,2?)
# Your code:

print(pd.concat([df_day1, df_day2]))

# Ex 5. Same stack, but pass ignore_index=True. Print the result and
#       compare the index to Ex 4.
# Your code:

print(pd.concat([df_day1, df_day2], ignore_index=True))

# -------------------------------------------------------------------
# BLOCK 4 — merge: SQL-style join on a key
# -------------------------------------------------------------------
#
# df.merge(other, on="key") joins two DataFrames on a shared column.
#
#   df.merge(df2, on="coin")                  → inner join (default)
#   df.merge(df2, on="coin", how="left")      → left join
#   df.merge(df2, on="coin", how="outer")     → full outer join
#   df.merge(df2, left_on="a", right_on="b")  → join on differently-named keys
#
# Think of `df` and `df2`:
#   df  has crypto prices (with `coin` column)
#   df2 has coin metadata (with `coin`, category, launch_year)
# We want each price row enriched with its coin's category/launch_year.


# Ex 6. Inner join df with df2 on `coin`. Print the result.
#       (df2 has "cardano" but df doesn't — confirm cardano is NOT in the output.)
# Your code:

print(df.merge(df2, on="coin"))


# Ex 7. Left join df with df2 on `coin` so we keep all of df's rows
#       even if a coin is missing from df2. Print the result.
#       (For our data, the result is the same as Ex 6 — but the SEMANTICS differ.)
# Your code:

print(df.merge(df2, on="coin", how="left"))

# Ex 8. Outer join df with df2 on `coin`. Print the result.
#       (Cardano should appear here, with NaN in df's columns.)
# Your code:

print(df.merge(df2, on="coin", how="outer"))