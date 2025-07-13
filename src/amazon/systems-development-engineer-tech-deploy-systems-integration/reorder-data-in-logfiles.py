"""
You are given an array of logs. Each log is a space-delimited string of words, where the first word is the identifier.

There are two types of logs:

Letter-logs: All words (except the identifier) consist of lowercase English letters.
Digit-logs: All words (except the identifier) consist of digits.
Reorder these logs so that:

The letter-logs come before all digit-logs.
The letter-logs are sorted lexicographically by their contents. If their contents are the same, then sort them lexicographically by their identifiers.
The digit-logs maintain their relative ordering.
Return the final order of the logs.

Example 1:
Input: logs = ["dig1 8 1 5 1","let1 art can","dig2 3 6","let2 own kit dig","let3 art zero"]
Output: ["let1 art can","let3 art zero","let2 own kit dig","dig1 8 1 5 1","dig2 3 6"]

Example 2:

Input: logs = ["a1 9 2 3 1","g1 act car","zo4 4 7","ab1 off key dog","a8 act zoo"]
Output: ["g1 act car","a8 act zoo","ab1 off key dog","a1 9 2 3 1","zo4 4 7"]
"""


def reorder_log_files(logs):
    letter_logs = []
    digit_logs = []
    
    for log in logs:
        identifier, content = log.split(" ", 1)
        
        if content[0].isdigit():
            digit_logs.append(log)
            
        else: letter_logs.append(log)
             
    letter_logs.sort(key = lambda log: (log.split(" ", 1)[1], log.split(" ", 1)[0]))

    return letter_logs + digit_logs

if __name__ == "__main__":
        
    logs = ["dig1 8 1 5 1",
        "let1 art can",
        "dig2 3 6",
        "let2 own kit dig",
        "let3 art zero"]

    print(reorder_log_files(logs))
