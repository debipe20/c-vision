"""
5. Longest Palindromic Substring
A palindromic string (or simply a palindrome) is a string that reads the same forward and backward.
Given a string s, return the longest palindromic substring in s

Input: s = "babad"
Output: "bab"
Explanation: "aba" is also a valid answer.
"""

def longestPalindrome(s: str) -> str:
    def expandAroundCenter(left: int, right: int) -> str: #This function tries to expand outward from the center left and right.
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return s[left + 1:right]  # Return the valid palindrome substring

    longest = ""
    for i in range(len(s)):
        # Odd length palindromes (centered at one letter)
        odd_pal = expandAroundCenter(i, i)
        # Even length palindromes (centered between two letters)
        even_pal = expandAroundCenter(i, i + 1)

        # Update the longest if needed
        if len(odd_pal) > len(longest):
            longest = odd_pal
        if len(even_pal) > len(longest):
            longest = even_pal

    return longest

s = "babad"
print(longestPalindrome(s))
