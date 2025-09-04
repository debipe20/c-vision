"""
Bubble Sort repeatedly steps through the list, compares adjacent elements, and swaps them if they are in the wrong order.
After each pass, the largest unsorted element "bubbles" up to its correct position.
nums = [5, 3, 8, 4, 2]
print(bubble_sort(nums))
"""

def bubble_sort(arr):
    n = len(arr)
           
    for i in range(n):  # Outer loop for each pass
        swapped = False

        for j in range(0, n - i - 1):  # Inner loop for comparison
            if arr[j] > arr[j + 1]:
                # Swap if the element is greater than the next
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        # If no two elements were swapped, the array is sorted
        if not swapped:
            break

    return arr

if __name__ == "__main__":
    nums = [5, 3, 8, 4, 2]
    print(bubble_sort(nums))