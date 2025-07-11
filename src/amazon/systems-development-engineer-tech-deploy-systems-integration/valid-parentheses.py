"""
valid-parentheses
Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:

Open brackets must be closed by the same type of brackets.

Open brackets must be closed in the correct order.

Every close bracket has a corresponding open bracket of the same type.
"""

class Validation:
    def __init__(self):
        pass
    
    def is_valid(self, string):
        
        stack = []
        close_map = {')': '(', ']': '[', '}': '{'}
        
        for char in string:
            if char in close_map:
                top = stack.pop() if stack else '#'
                
                if close_map[char] != top:
                    return False
                
                else:
                    stack.append(char)
                    
        return not stack
    
class Solution():
    def __init__(self):
        pass
    def isValid(self, s):
        stack = []
        close_map = {')': '(', ']': '[', '}': '{'}

        for char in s:
            if char in close_map:
                top = stack.pop() if stack else '#' #If the stack is not empty, pop the last opened bracket. If the stack is empty, we use a dummy character '#' to avoid a crash.
                if close_map[char] != top: # Check if the top (e.g.'(') of the stack is the correct opening for the closing bracket. Example: close_map[char] = '(' for char =')'
                    return False
            else:
                stack.append(char)

        return not stack #If the stack is empty, that means all brackets were matched correctl

# Create an instance of Solution
sol = Solution()

# Call the method properly
print(sol.isValid("()[]{}"))      # True
print(sol.isValid("([)]"))        # False
print(sol.isValid("{[]}"))        # True
print(sol.isValid("((("))         # False
