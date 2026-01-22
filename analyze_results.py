"""
Quick analysis script to analyze results.json
Calculates average return and target achievement rate
"""

import json
import statistics

def analyze_results():
    with open('results.json', 'r') as f:
        results = json.load(f)
    
    # Extract data
    returns = []
    target_achieved = []
    final_balances = []
    days_with_trades = []
    days_without_trades = []
    
    for date, data in results.items():
        return_pct = data['total_return_pct']
        balance = data['final_balance']
        achieved = data['achieved_target']
        num_trades = data['num_trades']
        
        returns.append(return_pct)
        final_balances.append(balance)
        target_achieved.append(achieved)
        
        if num_trades > 0:
            days_with_trades.append(date)
        else:
            days_without_trades.append(date)
    
    # Calculate statistics
    total_days = len(results)
    target_count = sum(target_achieved)
    target_rate = (target_count / total_days) * 100
    
    avg_return = statistics.mean(returns)
    median_return = statistics.median(returns)
    min_return = min(returns)
    max_return = max(returns)
    
    avg_balance = statistics.mean(final_balances)
    median_balance = statistics.median(final_balances)
    min_balance = min(final_balances)
    max_balance = max(final_balances)
    
    # Print results
    print("=" * 80)
    print("RESULTS ANALYSIS - December 2025")
    print("=" * 80)
    print()
    
    print(f"Total Days Analyzed: {total_days}")
    print(f"Days with Trades: {len(days_with_trades)}")
    print(f"Days without Trades: {len(days_without_trades)}")
    print()
    
    print("-" * 80)
    print("TARGET ACHIEVEMENT ($1,000,000)")
    print("-" * 80)
    print(f"Days that achieved $1M target: {target_count} out of {total_days}")
    print(f"Success Rate: {target_rate:.2f}%")
    print()
    
    if target_count > 0:
        target_days = [date for date, data in results.items() if data['achieved_target']]
        print(f"Days that achieved target:")
        for date in sorted(target_days):
            balance = results[date]['final_balance']
            return_pct = results[date]['total_return_pct']
            print(f"  {date}: ${balance:,.2f} ({return_pct:,.2f}% return)")
    print()
    
    print("-" * 80)
    print("RETURN STATISTICS")
    print("-" * 80)
    print(f"Average Return: {avg_return:,.2f}%")
    print(f"Median Return: {median_return:,.2f}%")
    print(f"Minimum Return: {min_return:,.2f}%")
    print(f"Maximum Return: {max_return:,.2f}%")
    print()
    
    print("-" * 80)
    print("FINAL BALANCE STATISTICS")
    print("-" * 80)
    print(f"Average Final Balance: ${avg_balance:,.2f}")
    print(f"Median Final Balance: ${median_balance:,.2f}")
    print(f"Minimum Final Balance: ${min_balance:,.2f}")
    print(f"Maximum Final Balance: ${max_balance:,.2f}")
    print()
    
    # Additional insights
    print("-" * 80)
    print("ADDITIONAL INSIGHTS")
    print("-" * 80)
    
    # Days with best returns (top 5)
    sorted_by_return = sorted(results.items(), key=lambda x: x[1]['total_return_pct'], reverse=True)
    print("\nTop 5 Days by Return:")
    for i, (date, data) in enumerate(sorted_by_return[:5], 1):
        print(f"  {i}. {date}: {data['total_return_pct']:,.2f}% (${data['final_balance']:,.2f})")
    
    # Days with worst returns (bottom 5)
    print("\nBottom 5 Days by Return:")
    for i, (date, data) in enumerate(sorted_by_return[-5:], 1):
        print(f"  {i}. {date}: {data['total_return_pct']:,.2f}% (${data['final_balance']:,.2f})")
    
    # Parameter analysis
    print("\nMost Common Optimal Parameters:")
    param_counts = {}
    for date, data in results.items():
        if data['tp_sl_percent'] is not None:
            key = (data['tp_sl_percent'], data['leverage'], data['position_allocation'])
            param_counts[key] = param_counts.get(key, 0) + 1
    
    sorted_params = sorted(param_counts.items(), key=lambda x: x[1], reverse=True)
    print("  (TP/SL %, Leverage, Allocation) -> Count")
    for (tp_sl, lev, alloc), count in sorted_params[:5]:
        print(f"  ({tp_sl}%, {lev}x, {alloc*100:.0f}%) -> {count} days")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    analyze_results()

