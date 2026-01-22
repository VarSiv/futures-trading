"""
Quick test script to verify the simulator works on a single day.
Run this to test before processing all days.
"""

from trading_simulator import OptimalStrategyFinder

if __name__ == "__main__":
    finder = OptimalStrategyFinder()
    
    # Test on December 1st
    date = "2025-12-01"
    print(f"Testing simulator on {date}...")
    print("This will test all parameter combinations and may take a few minutes.\n")
    
    result = finder.find_optimal_strategy(date, target_balance=1000000.0)
    
    print(f"\n{'='*60}")
    print(f"Results for {date}:")
    print(f"{'='*60}")
    print(f"Initial Balance: $10,000.00")
    print(f"Final Balance: ${result['final_balance']:,.2f}")
    print(f"Total Return: {(result['final_balance'] / 10000 - 1) * 100:.2f}%")
    print(f"\nOptimal Parameters:")
    print(f"  TP/SL: {result['tp_sl_percent']}%")
    print(f"  Leverage: {result['leverage']}x")
    print(f"  Position Allocation: {result.get('position_allocation', 0.9) * 100:.0f}%")
    print(f"\nTarget Achieved ($1M): {'YES' if result['achieved_target'] else 'NO'}")
    print(f"Number of Trades: {len(result['trades'])}")
    
    if result['trades']:
        print(f"\nFirst 5 trades:")
        for i, trade in enumerate(result['trades'][:5], 1):
            print(f"  {i}. {trade['symbol']} {trade['type']} @ ${trade['entry_price']:,.2f} -> "
                  f"${trade['exit_price']:,.2f} | PnL: ${trade['pnl']:,.2f}")

