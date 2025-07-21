"""
973. K Closest Points to Origin

Given an array of points where points[i] = [xi, yi] represents a point on the X-Y plane and an integer k, return the k closest points to the origin (0, 0).

The distance between two points on the X-Y plane is the Euclidean distance (i.e., √(x1 - x2)2 + (y1 - y2)2).

You may return the answer in any order. The answer is guaranteed to be unique (except for the order that it is in).

Input: points = [[1,3],[-2,2]], k = 1
Output: [[-2,2]]
Explanation:
The distance between (1, 3) and the origin is sqrt(10).
The distance between (-2, 2) and the origin is sqrt(8).
Since sqrt(8) < sqrt(10), (-2, 2) is closer to the origin.
We only want the closest k = 1 points from the origin, so the answer is just [[-2,2]]
"""


import heapq
 
def kClosest(points, k):
    max_heap = []

    for x, y in points:
        dist = -(x**2 + y**2)  # negative for max-heap behavior
        heapq.heappush(max_heap, (dist, [x, y])) #This ensures that the smallest element is always at index 0 (the top of the heap)
        
        if len(max_heap) > k:
            heapq.heappop(max_heap)  # remove farthest point (index 0)

    return [point for (_, point) in max_heap]

if __name__ == "__main__":
    # points = [[1,3],[-2,2]] 
    # k = 1
    points = [[3,3],[5,-1],[-2,4]]
    k = 1

    print(kClosest(points, k))  # Output: [[-2, 2]]
