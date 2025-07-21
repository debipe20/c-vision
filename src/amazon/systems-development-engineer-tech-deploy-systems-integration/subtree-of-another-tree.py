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
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def isSubtree(root, subRoot):
    if not root:
        return False

    if isSameTree(root, subRoot): #Check if the tree rooted at root is exactly the same as subRoot
        return True

    return isSubtree(root.left, subRoot) or isSubtree(root.right, subRoot)

def isSameTree(s, t):
    if not s and not t: # If both s (root) and t (subroot) are None, that means both trees have ended at this branch at the same time, which is good. They're equal in this path
        return True
    if not s or not t: #If only one of them is None, and the other one is not, the structure of the trees differs. That means they're not the same tree.
        return False
    if s.val != t.val:
        return False

    return isSameTree(s.left, t.left) and isSameTree(s.right, t.right)


def build_tree(values):
    if not values:
        return None

    root = TreeNode(values[0]) #Create the root node from the first value.
    queue = deque([root]) #Use queue to process nodes level by level.
    i = 1

    while queue and i < len(values): #Loop until all values are processed.
        node = queue.popleft() #Pop a node from the queue to assign its children.

        # Left child
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1

        # Right child
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1

    return root


if __name__ == "__main__":
    root_list = [3, 4, 5, 1, 2]
    sub_root_list = [4, 1, 2]

    root = build_tree(root_list)
    sub_root = build_tree(sub_root_list)

    print(isSubtree(root, sub_root))  # Output: True
