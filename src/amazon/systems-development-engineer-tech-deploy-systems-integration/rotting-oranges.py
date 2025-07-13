"""
994. Rotting Oranges
You are given an m x n grid where each cell can have one of three values:

0 representing an empty cell,
1 representing a fresh orange, or
2 representing a rotten orange.
Every minute, any fresh orange that is 4-directionally adjacent to a rotten orange becomes rotten.

Return the minimum number of minutes that must elapse until no cell has a fresh orange. If this is impossible, return -1.
"""

from collections import deque

def orangesRotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque()
    fresh_count = 0

    # Step 1: Find all initially rotten oranges and count fresh ones
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))  # (row, col, minute). Add all rotten oranges to the queue.
            elif grid[r][c] == 1:
                fresh_count += 1 #Count all fresh oranges.

    # Step 2: Perform BFS from all rotten oranges
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    time = 0

    while queue:
        r, c, minute = queue.popleft() #Take one rotten orange from the queue to process.
        time = max(time, minute) # Track how many minutes have passed until the last rotting. Since each level of BFS means "one more minute passed," this keeps track of total time.

        for dr, dc in directions:
            nr, nc = r + dr, c + dc #Try moving to the up, down, left, and right neighbors.
            # Check bounds and if neighbor is fresh
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2  # rot it
                fresh_count -= 1
                queue.append((nr, nc, minute + 1))

    # Step 3: Check if all fresh oranges were rotted
    return time if fresh_count == 0 else -1

grid = [[2,1,1],[1,1,0],[0,1,1]]
# grid = [[2,1,1],[0,1,1],[1,0,1]]
print(orangesRotting(grid))