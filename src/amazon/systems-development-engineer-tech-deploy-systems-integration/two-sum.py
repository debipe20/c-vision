
def two_sum_method(arr, target_val):
    arr_length = len(arr)
    
    for i in range(arr_length):
        for j in range(i + 1, arr_length):
            if arr[i] + arr[j] == target_val:
                return i, j  # early return as soon as pair is found
    
    return -1, -1  # indicate no solution found (although the problem says one solution exists)


if __name__ == "__main__":
    nums = [2, 7, 11, 15]
    target = 17
    
    print(two_sum_method(nums, target))