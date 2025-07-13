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
        for j in range(i + 1, min(n, i + 1 + arr[i])): #j ranges from i+1 to (i+1 + arr[i]) (but not exceeding n).
            sub_jumps = dfs(j) #Recursively compute max jumps needed from index j.
            if sub_jumps != -1: #If none of the jumps from position i lead to a valid solution, then max_jumps stays -1.
                max_jumps = max(max_jumps, 1 + sub_jumps) # If we can reach the end from j, update the max jumps at index i. 1 + sub_jumps: one jump to reach j, plus whatever it takes from there to the end.

        memo[i] = max_jumps
        return max_jumps

    result = dfs(0)
    return result
     

def min_jump_to_end(arr):
    n = len(arr)
    if n == 1:
        return 0 #f the array has only one element, you're already at the end, so no jumps are needed.
    
    farthest = 0  # The farthest index you can reach so far
    end = 0       # The end of the current jump range
    jumps = 0     # Number of jumps made

    for i in range(n - 1):
        farthest = max(farthest, i + arr[i])
        
        if i == end: #If you've reached the end of your current jump range, it means it's time to increase jumps by 1. And update end to the new boundary farthest
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