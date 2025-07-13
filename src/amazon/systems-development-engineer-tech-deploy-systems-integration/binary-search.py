"""
704. Binary Search
Problem:
Given an array of integers nums which is sorted in ascending order, and a target value target, return the index if the target is found. If not, return -1.

You must write an algorithm with O(log n) runtime complexity.

Input: nums = [-1,0,3,5,9,12], target = 9  
Output: 4

Input: nums = [-1,0,3,5,9,12], target = 2  
Output: -1
"""

def binary_search(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1

nums = [-1, 0, 3, 5, 9, 12]
target = 9
print(binary_search(nums, target))  # Output: 4