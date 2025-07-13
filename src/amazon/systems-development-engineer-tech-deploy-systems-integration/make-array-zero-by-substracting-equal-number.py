"""
You are given a non-negative integer array nums. In one operation, you must:

Choose a positive integer x such that x is less than or equal to the smallest non-zero element in nums.
Subtract x from every positive element in nums.
Return the minimum number of operations to make every element in nums equal to 0

Input: nums = [1,5,0,3,5]
Output: 3
"""

def minimumOperations(nums):
    return len(set(x for x in nums if x > 0))

def minimumOperationsVerbose(nums):
    steps = 0
    nums = nums[:]  # copy to avoid changing original
    
    while any(n > 0 for n in nums):
        x = min(n for n in nums if n > 0)
        print(f"\nOperation {steps+1}: Subtract x = {x}")
        nums = [n - x if n > 0 else 0 for n in nums]
        print(f"After operation {steps+1}: {nums}")
        steps += 1

    print(f"\nTotal operations: {steps}")
    return steps

    
if __name__ == "__main__":
    num_list = [1,5,0,3,5]
    # minimumOperations(num_list)
    minimumOperationsVerbose(num_list)