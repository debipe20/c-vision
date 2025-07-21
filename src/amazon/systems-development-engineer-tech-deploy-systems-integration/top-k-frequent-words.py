"""
692. Top K Frequent Words
Given an array of strings words and an integer k, return the k most frequent strings.

Return the answer sorted by the frequency from highest to lowest. Sort the words with the same frequency by their lexicographical order.
"""

import collections

def topKFrequent(words, k):
    word_counts = collections.Counter(words)
    
    # Sort by (-freq, word)
    sorted_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
    
    # Return top k words only
    return [word for word, freq in sorted_words[:k]]


words = ["i","love","leetcode","i","love","coding"]
k = 2
print(topKFrequent(words, k))  # Output: ['i', 'love']


