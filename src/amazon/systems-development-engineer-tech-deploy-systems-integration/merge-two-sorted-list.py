"""
21. Merge Two Sorted Lists
You are given the heads of two sorted linked lists list1 and list2.

Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists.

Return the head of the merged linked list.
Input: list1 = [1,2,4], list2 = [1,3,4]
Output: [1,1,2,3,4,4]
"""

class ListNode:
    
    def __init__(self, val =0, next = None):
        self.val = val
        self.next = next
        
def merge_two_lists(list1, list2):
    dummy = ListNode(-1)
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
        current = current.next
        
    return dummy.next

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def mergeTwoLists(list1, list2):
    dummy = ListNode(-1) # dummy is a node with value -1 (or any placeholder value). A dummy node is used to simplify list-building (avoid handling special cases for the head).
    current = dummy

    while list1 and list2: #Continue until we reach the end of either list.
        if list1.val < list2.val:
            current.next = list1
            list1 = list1.next
        else:
            current.next = list2
            list2 = list2.next
        current = current.next

    current.next = list1 if list1 else list2 #When one list is exhausted, just attach the remaining part of the other list (it’s already sorted).
    return dummy.next #return the actual head of the merged list (right after the dummy node)

def build_linked_list(arr):
    dummy = ListNode()
    current = dummy
    for num in arr:
        current.next = ListNode(num)
        current = current.next
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
    
    merged = mergeTwoLists(list1, list2)
    print_linked_list(merged)


