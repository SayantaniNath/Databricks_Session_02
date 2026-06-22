"""
Pandas Lesson 1 — Part 1: Series basics
----------------------------------------

A Series is a labeled column of data. Think: one column of a spreadsheet.

RUN WITH:
    ~/myenv/bin/python ~/Downloads/finflow/practice_pandas_01.py

    iloc vs loc — both select rows/columns, but interpret the argument differently:

  ┌────────────────┬────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────┐
  │                │              df.iloc[...]              │                                      df.loc[...]                                       │
  ├────────────────┼────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ Uses           │ integer position (like array indexing) │ actual labels (index value, column name)                                               │
  ├────────────────┼────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ First row      │ df.iloc[0]                             │ df.loc[0] (if your index is 0, 1, 2...) — would be df.loc["abc"] if index were strings │
  ├────────────────┼────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ Slice end      │ exclusive (like Python lists)          │ inclusive                                                                              │
  ├────────────────┼────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ Rows 0,1,2     │ df.iloc[0:3]                           │ df.loc[0:2]                                                                            │
  ├────────────────┼────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ Column by name │ df.iloc[:, 2] (3rd column)             │ df.loc[:, "price_usd"]                                                                 │
  └────────────────┴────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────┘

  The end-exclusive vs end-inclusive thing is the #1 gotcha — Pandas chose loc to be inclusive because labels aren't always numbers (you can't "stop one before 'Tuesday'").

  ---
  list vs tuple — both hold ordered sequences, but:

  ┌───────────┬────────────────────────────────────────┬───────────────────────────────────────────────────────┐
  │           │                  list                  │                         tuple                         │
  ├───────────┼────────────────────────────────────────┼───────────────────────────────────────────────────────┤
  │ Syntax    │ [1, 2, 3]                              │ (1, 2, 3)                                             │
  ├───────────┼────────────────────────────────────────┼───────────────────────────────────────────────────────┤
  │ Mutable?  │ ✅ yes — can change, add, remove       │ ❌ no — frozen after creation                         │
  ├───────────┼────────────────────────────────────────┼───────────────────────────────────────────────────────┤
  │ Methods   │ .append(), .remove(), .pop(), etc.     │ only .count(), .index()                               │
  ├───────────┼────────────────────────────────────────┼───────────────────────────────────────────────────────┤
  │ Use when  │ the collection will grow/shrink/change │ the collection is fixed (coords, fixed-arity records) │
  ├───────────┼────────────────────────────────────────┼───────────────────────────────────────────────────────┤
  │ Hashable? │ ❌ can't be a dict key or set member   │ ✅ can be                                             │
  ├───────────┼────────────────────────────────────────┼───────────────────────────────────────────────────────┤
  │ Speed     │ slightly slower                        │ slightly faster                                       │
  └───────────┴────────────────────────────────────────┴───────────────────────────────────────────────────────┘
  
  Common patterns:
  prices = [67123.45, 3210.10, 148.77]    # list — you might add more prices
  prices.append(150.0)                     # works
  
  point = (40.7, -74.0)                    # tuple — lat/lon, fixed pair
  point[0] = 41.0                          # TypeError — tuples are frozen
  
  Why this matters for Pandas: column-selection with df.iloc[0, 2] uses a tuple-like form (row, col). And dict keys (which Pandas index labels are like) must be hashable — that's why row labels can be
  tuples but not lists.
"""

import pandas as pd

# Make a Series of crypto prices
prices = pd.Series([67123.45, 3210.10, 148.77], name="price_usd")

prices2 = pd.Series( 
      [67123.45, 3210.10, 148.77],
      index=["bitcoin", "ethereum", "solana"],
      name="price_usd",
  )

print(prices)
print(prices2)
print(prices2["bitcoin"])
print(prices2[["bitcoin", "solana"]])

df = pd.DataFrame({
      "coin":      ["bitcoin", "ethereum", "solana"],
      "symbol":    ["btc", "eth", "sol"],
      "price_usd": [67123.45, 3210.10, 148.77],
  })

print(df)
print(df["coin"])           # one column → returns a Series
print(df[["coin", "price_usd"]])  # multiple columns → returns a smaller DataFrame
print(df.iloc[0])           # the first ROW → returns a Series


