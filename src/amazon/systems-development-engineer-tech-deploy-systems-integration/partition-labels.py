"""
763. Partition Labels

Hint
You are given a string s. We want to partition the string into as many parts as possible so that each letter appears in at most one part. For example, the string "ababcc" can be partitioned into ["abab", "cc"], but partitions such as ["aba", "bcc"] or ["ab", "ab", "cc"] are invalid.

Note that the partition is done so that after concatenating all the parts in order, the resultant string should be s.

Return a list of integers representing the size of these parts
"""

def partitionLabels(s: str):
    # Step 1: Record last occurrence of each character
    last = {char: idx for idx, char in enumerate(s)}
    
    result = []
    start = 0
    end = 0
    
    # Step 2: Iterate through string to find partitions
    for i, char in enumerate(s):
        end = max(end, last[char])  # Update end to farthest last occurrence
        if i == end:
            # We've reached the end of a partition
            result.append(end - start + 1)
            start = i + 1  # Start of next partition
    
    return result

s = "ababcbacadefegdehijhklij"
print(partitionLabels(s))  # Output: [9, 7, 8]
