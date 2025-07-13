"""
valid-parentheses
Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:

Open brackets must be closed by the same type of brackets.

Open brackets must be closed in the correct order.

Every close bracket has a corresponding open bracket of the same type.
"""


def is_valid(input_string):
    
    stack = []
    character_map = {'(': ')', '{': '}', '[': ']'}
    
    for char in input_string:
        if char in character_map:
            top = stack.pop() if stack else '#'
            
            if character_map[char] !=top:
                return False
            
        else:
            stack.append(char)
            
    return not stack