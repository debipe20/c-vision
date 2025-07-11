"""
138. Copy List with Random Pointer

A linked list of length n is given such that each node contains an additional random pointer, which could point to any node in the list, or null.

Construct a deep copy of the list. The deep copy should consist of exactly n brand new nodes, where each new node has its value set to the value of its corresponding original node. Both the next and random pointer of the new nodes should point to new nodes in the copied list such that the pointers in the original list and copied list represent the same list state. None of the pointers in the new list should point to nodes in the original list.

For example, if there are two nodes X and Y in the original list, where X.random --> Y, then for the corresponding two nodes x and y in the copied list, x.random --> y.

Return the head of the copied linked list.

The linked list is represented in the input/output as a list of n nodes. Each node is represented as a pair of [val, random_index] where:

val: an integer representing Node.val
random_index: the index of the node (range from 0 to n-1) that the random pointer points to, or null if it does not point to any node.
Your code will only be given the head of the original linked list

Input: head = [[7,null],[13,0],[11,4],[10,2],[1,0]]
Output: [[7,null],[13,0],[11,4],[10,2],[1,0]]
"""

class Node:
    def __init__(self, val, next=None, random=None):
        self.val = val
        self.next = next
        self.random = random

def build_linked_list(data):
    if not data:
        return None

    # Step 1: Create all nodes
    nodes = [Node(val) for val, _ in data]

    # Step 2: Set next pointers
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]

    # Step 3: Set random pointers
    for i, (_, random_index) in enumerate(data):
        if random_index is not None:
            nodes[i].random = nodes[random_index]

    return nodes[0]  # Return head of the list

def copyRandomList(head):
    if not head:
        return None

    old_to_new = {}

    # Step 1: Copy all nodes
    current = head
    while current:
        old_to_new[current] = Node(current.val)
        current = current.next

    # Step 2: Assign next and random pointers
    current = head
    while current:
        if current.next:
            old_to_new[current].next = old_to_new[current.next]
        if current.random:
            old_to_new[current].random = old_to_new[current.random]
        current = current.next

    return old_to_new[head]

def print_linked_list(head):
    result = []
    index_map = {}
    idx = 0
    node = head
    while node:
        index_map[node] = idx
        idx += 1
        node = node.next

    node = head
    while node:
        val = node.val
        rand_idx = index_map.get(node.random, None) if node.random else None
        result.append([val, rand_idx])
        node = node.next

    print(result)

# === Test ===
head_data = [[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]
head = build_linked_list(head_data)
copied = copyRandomList(head)
print_linked_list(copied)