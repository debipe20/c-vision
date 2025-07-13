"""
127. Word Ladder
A transformation sequence from word beginWord to word endWord using a dictionary wordList is a sequence of words beginWord -> s1 -> s2 -> ... -> sk such that:

Every adjacent pair of words differs by a single letter.
Every si for 1 <= i <= k is in wordList. Note that beginWord does not need to be in wordList.
sk == endWord
Given two words, beginWord and endWord, and a dictionary wordList, return the number of words in the shortest transformation sequence from beginWord to endWord, or 0 if no such sequence exists.
"""

from collections import deque

def ladderLength(beginWord, endWord, wordList):
    # Convert wordList to a set for faster lookup
    wordSet = set(wordList)

    # If the endWord is not in the dictionary, transformation is impossible
    if endWord not in wordSet:
        return 0

    # Initialize a queue for BFS, with (word, current transformation length)
    queue = deque()
    queue.append((beginWord, 1))  # Start from beginWord with 1 step

    while queue:
        current_word, level = queue.popleft()

        # Try changing each letter of current_word to every letter from 'a' to 'z'
        for i in range(len(current_word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                # Generate a new word by replacing the i-th character
                next_word = current_word[:i] + c + current_word[i+1:]

                # If next_word matches the endWord, return the level + 1
                if next_word == endWord:
                    return level + 1

                # If the next_word is in the dictionary
                if next_word in wordSet:
                    # Remove it from the set to prevent revisiting
                    wordSet.remove(next_word)
                    # Add it to the queue with an increased level
                    queue.append((next_word, level + 1))

    # If BFS completes without finding endWord, return 0
    return 0
