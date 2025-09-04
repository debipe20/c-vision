"""
146. LRU Cache
An LRU (Least Recently Used) Cache is a type of data structure that stores a limited number of key-value pairs and automatically removes the least recently used item when the capacity is exceeded.

Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

Implement the LRUCache class:

LRUCache(int capacity) Initialize the LRU cache with positive size capacity.
int get(int key) Return the value of the key if the key exists, otherwise return -1.
void put(int key, int value) Update the value of the key if the key exists. Otherwise, add the key-value pair to the cache.
If the number of keys exceeds the capacity from this operation, evict the least recently used key.

The functions get and put must each run in O(1) average time complexity.
"""

from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # Move the key to the end of the OrderedDict, marking it as recently used.

        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key) #If key already exists, move it to the end to mark it as recently used.
            
        self.cache[key] = value
        
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # Remove least recently used
            
lru = LRUCache(2)
lru.put(1, 1)
lru.put(2, 2)
print(lru.get(1))  # Output: 1 (mark 1 as recently used)
lru.put(3, 3)      # Evicts key 2 (least recently used)
print(lru.get(2))  # Output: -1 (not found)
lru.put(4, 4)      # Evicts key 1
print(lru.get(1))  # Output: -1
print(lru.get(3))  # Output: 3
print(lru.get(4))  # Output: 4
