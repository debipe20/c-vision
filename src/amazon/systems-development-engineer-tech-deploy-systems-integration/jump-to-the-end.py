"""
Problem:
You are given an array of non-negative integers nums of length n. A pawn is placed at index 0 (1st position). 
The value at each index i represents the maximum number of steps the pawn can jump forward from that position.
From index i, you can jump to any index from i+1 to i + A[i].

If A[i] == 0, you're stuck.
Your task is to:
1. Determine if it's possible to reach the last index (n - 1) from the start.
2. If possible, return the maximum & minimum number of jumps used to reach the end.
3. If not possible, return -1
"""

def max_jumps_to_end(arr):
    n = len(arr)
    memo = {}

    def dfs(i):
        if i == n - 1:
            return 0  # Reached end, no more jumps
        if i in memo:
            return memo[i]

        max_jumps = -1  # Start with invalid case
        for j in range(i + 1, min(n, i + arr[i] + 1)): #j ranges from i+1 to i + arr[i] (but not exceeding n).
            sub_jumps = dfs(j) #Recursively compute max jumps needed from index j.
            if sub_jumps != -1:
                max_jumps = max(max_jumps, 1 + sub_jumps) # If we can reach the end from j, update the max jumps at index i. 1 + sub_jumps: one jump to reach j, plus whatever it takes from there to the end.

        memo[i] = max_jumps
        return max_jumps

    result = dfs(0)
    return result


def min_jump_to_end(nums):
    n = len(nums)
    if n == 1:
        return 0
    
    farthest = 0
    end = 0
    jumps = 0

    for i in range(n - 1):
        farthest = max(farthest, i + nums[i])
        
        if i == end:
            jumps += 1
            end = farthest
        
        if end >= n - 1:
            return jumps
    
    return -1


arr = [2, 3, 1, 1, 4]
print(max_jumps_to_end(arr)) 
# print(min_jump_to_end(arr))

# arr = [3, 2, 1, 0, 4]
# print(max_jumps_to_end(arr))  # Output: -1 (cannot reach end)
# print(min_jump_to_end(arr))