"""
240. Search a 2D Matrix II
Write an efficient algorithm that searches for a value target in an m x n integer matrix matrix. This matrix has the following properties:
Integers in each row are sorted in ascending from left to right.
Integers in each column are sorted in ascending from top to bottom.
Input: matrix = [[1,4,7,11,15],[2,5,8,12,19],[3,6,9,16,22],[10,13,14,17,24],[18,21,23,26,30]], target = 5
Output: true
"""

def searchMatrix(matrix, target):
    if not matrix or not matrix[0]:
        return False

    rows = len(matrix)
    cols = len(matrix[0])

    # Start from top-right corner
    row = 0
    col = cols - 1

    while row < rows and col >= 0:
        curr = matrix[row][col]

        if curr == target:
            return True
        elif curr > target:
            col -= 1  # Move left
        else:
            row += 1  # Move down

    return False


matrix = [
  [1,4,7,11,15],
  [2,5,8,12,19],
  [3,6,9,16,22],
  [10,13,14,17,24],
  [18,21,23,26,30]
]
target = 5

print(searchMatrix(matrix, target))  # Output: True
