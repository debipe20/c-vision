"""
572. Subtree of Another Tree
Hint
Given the roots of two binary trees root and subRoot, return true if there is a subtree of root with the same structure and node values of subRoot and false otherwise.
A subtree of a binary tree is a tree that consists of a node in tree and all of this node's descendants. The tree could also be considered as a subtree of itself.

Input: root = [3,4,5,1,2], subRoot = [4,1,2]
Output: true
"""
from collections import deque
class TreeNode:
    def __init__(self, val=0, left =None, right = None):
        self.val = val
        self.left = left
        self.right = right
        
def build_tree(values):
    
    if not values:
        return None
    
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i <len(values) and node.val is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
            
        i+=1
        
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1

    return root

def isSubTree(root, subroot):
    if not root:
        return False
    if isSameTree(root, subroot):
        return True
    
    return isSubTree(root.left, subroot) or isSubTree(root.right, subroot)
    
def isSameTree(s,t):
    if not s and not t:
        return True
    
    if not s or not t:
        return False
    
    if s.val!=t.val:
        return False
    
    return isSameTree(s.left, t.left) or isSameTree(s.right, t.right)

if __name__ == "__main__":
    root_list = [3, 4, 5, 1, 2]
    sub_root_list = [4, 1, 2]

    root = build_tree(root_list)
    sub_root = build_tree(sub_root_list)

    print(isSubTree(root, sub_root))  # Output: True