"""
819. Most Common Word
Given a string paragraph and a string array of the banned words banned, return the most frequent word that is not banned. It is guaranteed there is at least one word that is not banned, and that the answer is unique.

The words in paragraph are case-insensitive and the answer should be returned in lowercase.

Note that words can not contain punctuation symbols.
Input: paragraph = "Bob hit a ball, the hit BALL flew far after it was hit.", banned = ["hit"]
Output: "ball"
"""

import collections
import re

def mostCommonWord(paragraph, banned):
    # Step 1: Normalize paragraph. Convert to lowercase for case-insensitive comparison
    paragraph = paragraph.lower()
    
    # Step 2: Extract words (ignore punctuation). \w+ matches any word characters (letters and numbers). So this removes punctuation automatically
    words = re.findall(r'\w+', paragraph)

    # Step 3: Count words excluding banned. Convert list to set for fast lookup (O(1) access)
    banned_set = set(banned)
    word_counts = collections.Counter(word for word in words if word not in banned_set) #Count only the non-banned words

    # Step 4: Return the most common word
    return word_counts.most_common(1)[0][0]


paragraph = "Bob hit a ball, the hit BALL flew far after it was hit."
banned = ["hit"]
print(mostCommonWord(paragraph, banned))