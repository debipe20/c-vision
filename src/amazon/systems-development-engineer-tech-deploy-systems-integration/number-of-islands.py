def numIslands(grid):
    
    if not grid or not grid[0]: # Edge case: if the grid is empty or has empty rows, return 0 immediately.
        return 0

    rows = len(grid)
    cols = len(grid[0])
    count = 0

    def dfs(r, c):

        if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] == '0':
            return
        
        grid[r][c] = '0'  # mark as visited
        
        # explore all 4 directions
        dfs(r + 1, c)  # down
        dfs(r - 1, c)  # up
        dfs(r, c + 1)  # right
        dfs(r, c - 1)  # left

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)

    return count

grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]

# print(numIslands(grid))  # Output: 3
print(num_of_islands(grid))