"""
main script to solve the trading problem for all days in december 2025
determines maximum achievable profit and optimal parameters for each day
"""

import os
from datetime import datetime, timedelta
from trading_simulator import OptimalStrategyFinder
import json


def generate_dates_in_december_2025():
    dates = []
    start_date = datetime(2025, 12, 1)
    for i in range(31):
        date = start_date + timedelta(days=i)
        dates.append(date.strftime("%Y-%m-%d"))
    return dates


def main():
    finder = OptimalStrategyFinder()
    
    results = {}
    dates = generate_dates_in_december_2025()
    
    print("=" * 80)
    print("CRYPTOCURRENCY FUTURES TRADING SIMULATOR")
    print("Analyzing all days in December 2025")
    print("=" * 80)
    print()
    
    for date_str in dates:
        print(f"\n{'='*80}")
        print(f"Processing: {date_str}")
        print(f"{'='*80}")
        
        result = finder.find_optimal_strategy(date_str, target_balance=1000000.0)
        
        results[date_str] = result
        
        print(f"\nResults for {date_str}:")
        print(f"  Initial Balance: $10,000.00")
        print(f"  Final Balance: ${result['final_balance']:,.2f}")
        print(f"  Total Return: {(result['final_balance'] / 10000 - 1) * 100:.2f}%")
        allocation_pct = (result.get('position_allocation') or 0.9) * 100
        tp_sl_str = f"{result['tp_sl_percent']}%" if result['tp_sl_percent'] else "N/A"
        leverage_str = f"{result['leverage']}x" if result['leverage'] else "N/A"
        print(f"  Optimal Parameters: {tp_sl_str} TP/SL, {leverage_str} leverage, {allocation_pct:.0f}% allocation")
        print(f"  Target Achieved ($1M): {'YES' if result['achieved_target'] else 'NO'}")
        print(f"  Number of Trades: {len(result['trades'])}")
    
    output_file = "results.json"
    json_results = {}
    for date, result in results.items():
        json_results[date] = {
            'final_balance': result['final_balance'],
            'initial_balance': 10000.0,
            'total_return_pct': (result['final_balance'] / 10000 - 1) * 100,
            'tp_sl_percent': result['tp_sl_percent'],
            'leverage': result['leverage'],
            'position_allocation': result.get('position_allocation') or 0.9,
            'achieved_target': result['achieved_target'],
            'num_trades': len(result['trades']),
            'trades': result['trades']
        }
    
    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    target_days = [date for date, result in results.items() if result['achieved_target']]
    max_balance_day = max(results.items(), key=lambda x: x[1]['final_balance'])
    
    print(f"\nDays where $1,000,000 was achieved: {len(target_days)}")
    if target_days:
        print(f"  {', '.join(target_days)}")
    else:
        print(f"  None")
    
    print(f"\nMaximum balance achieved: ${max_balance_day[1]['final_balance']:,.2f}")
    print(f"  Day: {max_balance_day[0]}")
    allocation_pct = (max_balance_day[1].get('position_allocation') or 0.9) * 100
    tp_sl_str = f"{max_balance_day[1]['tp_sl_percent']}%" if max_balance_day[1]['tp_sl_percent'] else "N/A"
    leverage_str = f"{max_balance_day[1]['leverage']}x" if max_balance_day[1]['leverage'] else "N/A"
    print(f"  Parameters: {tp_sl_str} TP/SL, {leverage_str} leverage, {allocation_pct:.0f}% allocation")
    
    print(f"\nResults saved to: {output_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

