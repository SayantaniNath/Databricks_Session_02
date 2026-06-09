# Python Problem Log

| Date | Problem | Pattern | Solved from blank? | Notes |
|---|---|---|---|---|
| 2026-06-03 | Two Sum | Arrays & Hashing | With hints | Understood hashmap approach; needed help with enumerate, seen[complement] lookup, and indentation |

---

## Two Sum

**Problem:** Given a list of integers `nums` and an integer `target`, return the indices of the two numbers that add up to `target`. Exactly one solution exists.

```
Example:
nums = [2, 7, 11, 15], target = 9
Output: [0, 1]  # nums[0] + nums[1] = 9
```

**Solution (hashmap — O(n) time, O(n) space):**

```python
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
```

**How it works:**
- Walk through the list once
- For each number, calculate its complement (`target - num`)
- Check if the complement was already seen — if yes, return both indices
- Otherwise store the current number and its index in `seen`
- `seen[num] = i` stores number as key, index as value — so `seen[complement]` retrieves the index

**Brute force (O(n²) — too slow):**

```python
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
```

---

## Q&A — 2026-06-03

**Q: What is O(n) and O(n²)?**
O(n) means you touch each element once — 1000 items = ~1000 operations. O(n²) means for each element you check every other element — 1000 items = ~1,000,000 operations. Dictionary lookup is O(1) (instant), which is why the hashmap solution is O(n) overall. Always state time + space complexity after writing a solution in interviews.

**Q: What does `enumerate(nums)` do?**
Gives you both the index and value in one line as you loop. `for i, num in enumerate([2,7,11,15])` produces pairs `(0,2), (1,7), (2,11), (3,15)`. Without it you'd need `for i in range(len(nums)): num = nums[i]` — two lines instead of one.

**Q: What does `seen[complement]` return?**
It returns the index where that complement was previously stored. `seen = {2: 0}` means the number `2` was found at index `0`. So `seen[2]` returns `0`. The key is the number, the value is its index.

**Q: What do `return [seen[complement], i]` and `seen[num] = i` do?**
- `seen[num] = i` — stores the current number and its index into the dict ("I saw number `num` at index `i`")
- `return [seen[complement], i]` — when the complement is found, retrieves the index where it was stored and pairs it with the current index

**Q: Why return a list `[...]` and not a tuple `(...)`?**
The problem asks for a list. `[0, 1]` is a list, `(0, 1)` is a tuple. Both work in practice but use square brackets to match the expected output type.
