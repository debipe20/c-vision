"""
Find the maximum value that the sum of two elements in an array is less than k

Input
numerals : array
k : k in question
Output
Maximum value less than k, if not -1
"""
def two_sum_less_than_k(arr, k):
    max_sum = -1
    n = len(arr)
    
    for i in range(n):
        for j in range(i + 1, n):
            pair_sum = arr[i] + arr[j]
            if pair_sum < k:
                max_sum = max(max_sum, pair_sum)
    
    return max_sum


arr = [34, 23, 1, 24, 75, 33, 54, 8]
k = 60
print(two_sum_less_than_k(arr, k))  # Output: 58