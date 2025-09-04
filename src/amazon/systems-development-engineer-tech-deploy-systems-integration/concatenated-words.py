"""
472. Concatenated Words
Given an array of strings words (without duplicates), return all the concatenated words in the given list of words.

A concatenated word is defined as a string that is comprised entirely of at least two shorter words (not necessarily distinct) in the given array.

Input: words = ["cat","cats","catsdogcats","dog","dogcatsdog","hippopotamuses","rat","ratcatdogcat"]
Output: ["catsdogcats","dogcatsdog","ratcatdogcat"]
Explanation: "catsdogcats" can be concatenated by "cats", "dog" and "cats"; 
"dogcatsdog" can be concatenated by "dog", "cats" and "dog"; 
"ratcatdogcat" can be concatenated by "rat", "cat", "dog" and "cat"
"""

def findAllConcatenatedWordsInADict(words):
    word_set = set(words)  # To enable fast lookup
    memo = {}

    def canForm(word):
        if word in memo:
            return memo[word] #If we’ve already checked this word, return its stored result directly to save time
        
        for i in range(1, len(word)):
            prefix = word[:i]
            suffix = word[i:]

            if prefix in word_set:
                if suffix in word_set or canForm(suffix):
                    memo[word] = True
                    return True

        memo[word] = False
        return False

    result = []

    for word in words: 
        if not word: #Skip any empty string (edge case).
            continue
        word_set.remove(word)  # Temporarily remove to prevent self-use
        if canForm(word):
            result.append(word)
        word_set.add(word)  # Restore it back

    return result

words = ["cat","cats","catsdogcats","dog","dogcatsdog","hippopotamuses","rat","ratcatdogcat"]
print(findAllConcatenatedWordsInADict(words))