# Python Problem Log

| Date | Problem | Pattern | Solved from blank? | Notes |
|---|---|---|---|---|
| 2026-06-03 | Two Sum | Arrays & Hashing | With hints | Understood hashmap approach; needed help with enumerate, seen[complement] lookup, and indentation |
| 2026-06-11 | Group Anagrams | Arrays & Hashing | Mostly — got logic right, needed syntax fixes (colon, sorted vs sort) | Understood defaultdict(list), sorted key fingerprint, and append pattern |

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

---

## Group Anagrams
*Date: 2026-06-11 | Pattern: Arrays & Hashing*

**Problem:** Given a list of strings, group the anagrams together. Return groups in any order.

```
Example:
Input:  ["eat","tea","tan","ate","nat","bat"]
Output: [["eat","tea","ate"], ["tan","nat"], ["bat"]]
```

**Solution (defaultdict + sorted key — O(n·k log k) time, O(n·k) space):**

```python
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)      # dict that auto-creates [] for any new key
    for word in strs:               # loop through each word
        key = "".join(sorted(word)) # sort letters → anagram fingerprint: "eat" → "aet"
        groups[key].append(word)    # add word to its bucket
    return list(groups.values())    # return all buckets as list of lists
```

**How it works:**
- All anagrams produce the same sorted string ("eat", "tea", "ate" all → "aet")
- Use that sorted string as the dict key → all anagrams land in the same bucket
- `defaultdict(list)` auto-creates `[]` on first access so `.append()` never crashes

---

## Q&A — 2026-06-11

**Q: Why does a plain dict crash but defaultdict works?**
`{}["newkey"].append("x")` → KeyError because "newkey" doesn't exist yet. `defaultdict(list)["newkey"].append("x")` works because it auto-creates `[]` at "newkey" the first time it's accessed.

**Q: What does `sorted(word)` return?**
A list of characters sorted alphabetically. `sorted("eat")` → `['a', 'e', 't']`. Not a string — that's why you need `"".join(...)` to turn it back.

**Q: What does `"".join(sorted(word))` do?**
`"".join(...)` joins a list of strings into one string using `""` (nothing) as separator. `['a','e','t']` → `"aet"`. If you used `",".join(...)` you'd get `"a,e,t"` — also a valid key but `""` is cleaner.

**Q: How is `groups.values()` different from `groups`?**
`groups` is the full dict e.g. `{"aet": ["eat","tea"], "abt": ["bat"]}`. `groups.values()` gives just the values (the buckets): `[["eat","tea"], ["bat"]]`. Wrap in `list()` to return as a plain list.
