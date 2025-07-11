"""
121. Best Time to Buy and Sell Stock
You are given an array prices where prices[i] is the price of a given stock on the ith day.

You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.

Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.
Input: prices = [7,1,5,3,6,4]
Output: 5
"""

def maxProfit(prices):
    min_price = float('inf')  # Initialize to positive infinity
    max_profit = 0

    for price in prices:
        if price < min_price:
            min_price = price  # Update minimum price if a lower price is found
        else:
            profit = price - min_price
            max_profit = max(max_profit, profit)  # Update max profit if current profit is higher

    return max_profit

prices = [7,1,5,3,6,4]
print(maxProfit(prices))  # Output: 5