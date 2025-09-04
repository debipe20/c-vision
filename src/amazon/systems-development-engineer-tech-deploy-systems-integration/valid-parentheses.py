"""
valid-parentheses
Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:

Open brackets must be closed by the same type of brackets.

Open brackets must be closed in the correct order.

Every close bracket has a corresponding open bracket of the same type.
"""

def isValid(input_string):
    stack = []
    character_map = {')': '(', ']': '[', '}': '{'}

    for char in input_string:
        if char in character_map:
            top = stack.pop() if stack else '#' #If the stack is not empty, pop the last opened bracket. If the stack is empty, we use a dummy character '#' to avoid a crash.
            if character_map[char] != top: # Check if the top (e.g.'(') of the stack is the correct opening for the closing bracket. Example: character_map[char] = '(' for char =')'
                return False
        else:
            stack.append(char)

    return not stack #If the stack is empty, that means all brackets were matched correctl


# Call the method properly
print(isValid("()[]{}"))      # True
print(isValid("([)]"))        # False
print(isValid("{[]}"))        # True
print(isValid("((("))         # False
