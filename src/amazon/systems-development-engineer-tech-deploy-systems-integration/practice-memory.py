
class ListNode:
    def __init__ (self, val = 0, next =  None):
        self.val = val
        self.next = next

def merge_two_list(list1, list2):
    dummy = ListNode()
    current = dummy
    
    while list1 and list2:
        
        if list1.val < list2.val:
            current.next = list1
            list1 = list1.next
            
        else:
            current.next = list2
            list2 = list2.next
        current = current.next
        
    current.next = list1 if list1 else list2
    
    return dummy.next

def build_linked_list(arr):
    dummy = ListNode()
    current = dummy
    
    for num in arr:
        current.next = ListNode(num)
        current  = current.next
        
    return dummy.next

def print_linked_list(head):
    result = []
    
    while head:
        result.append(head.val)
        head = head.next
        
    print(result)
    
if __name__ == "__main__":
    list1 = build_linked_list([1, 2, 4])
    list2 = build_linked_list([1, 3, 4])
    
    merged = merge_two_list (list1, list2)
    print_linked_list(merged)
# import heapq

# def k_closest_point(points, k):
    
#     max_heap = []
    
#     for x, y in points:
#         dis = x**2 + y**2
        
#         heapq.heappush(max_heap, (-dis, (x,y)))
        
#         if len(max_heap) > k:
#             heapq.heappop(max_heap)
            
#     return [point for (_, point) in max_heap]


# if __name__ == "__main__":
#     # points = [[1,3],[-2,2]] 
#     # k = 1
#     points = [[3,3],[5,-1],[-2,4]]
#     k = 1

#     print(k_closest_point(points, k))  # Output: [[-2, 2]]




# import re
# import collections

# def most_common_word(paragraph, banned):
    
#     paragraph = paragraph.lower()
#     words = re.findall(r'\w+', paragraph)
    
    
#     banned_set = set(banned)
    
#     word_counts = collections.Counter(word for word in words if word not in banned_set)
    
#     return word_counts.most_common(1)[0][0]


# paragraph = "Bob hit a ball, the hit BALL flew far after it was hit."
# banned = ["hit"]
# print(most_common_word(paragraph, banned))





# from collections import deque


# def rotten_oranges_time(grid):
    
#     rows = len(grid)
#     cols = len(grid[0])
#     queue =deque()
#     fresh_count = 0
    
#     for r in range(rows):
#         for c in range(cols):
#             if grid[r][c] == 2:
#                 queue.append((r,c,0))
#             elif grid[r][c] == 1:
#                 fresh_count +=1
                
                
#     directions = [(0,1), (0,-1), (1,0), (-1,0)] 
#     time = 0
    
    
#     while queue:
        
#         r, c, minute = queue.popleft()
#         time = max(time, minute)
        
#         for dr, dc in directions:
#             nr, nc = r + dr, c + dc
            
#             if 0<=nr<rows and 0<=nc<cols and grid[nr][nc] == 1:
#                 grid[nr][nc] = 2
#                 queue.append((nr,nc,minute+1))
#                 fresh_count -=1
                
                
#     return time if fresh_count == 0 else -1    
       
# grid = [[2,1,1],[1,1,0],[0,1,1]]
# # grid = [[2,1,1],[0,1,1],[1,0,1]]
# print(rotten_oranges_time(grid))

# def number_of_island(grid):
    
#     if not grid or not grid[0]:
#         return 0
    
#     rows = len(grid)
#     cols = len(grid[0])
#     count = 0
    
    
#     def dfs(r,c):
        
#         if r <0 or c <0 or r >=rows or c>=cols or grid[r][c] == '0':
#             return
        
#         grid[r][c] = '0'
        
        
#         dfs(r,c+1)
#         dfs(r, c-1)
#         dfs(r+1,c)
#         dfs(r-1,c)
    
#     for r in range(rows):
#         for c in range(cols):
#             if grid[r][c] == '1':
#                 dfs(r,c)
#                 count +=1
                
#     return count

# grid = [
#   ["1","1","0","0","0"],
#   ["1","1","0","0","0"],
#   ["0","0","1","0","0"],
#   ["0","0","0","1","1"]
# ]


# print(number_of_island(grid))