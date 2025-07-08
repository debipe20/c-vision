###DP

def fib(n):
    if n <= 1:
        return n

    dp = [0] * (n + 1) # Create a list `dp` of length `n+1`, all initialized to `0`
    dp[1] = 1 # This list will **store the Fibonacci values** at each index `i`, i.e., `dp[i] = F(i)`

    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]

    return dp[n]

def fib(n):
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b

    return b
