# Cryptocurrency Futures Trading Simulator

## Problem Statement

Given perfect knowledge of all future price movements for BTCUSDT, ETHUSDT, and BNBUSDT futures within a 24-hour period, determine:

1. Whether it's possible to turn $10,000 into $1,000,000
2. If possible, the sequence of trades that achieves this
3. The maximum achievable profit for each day

## Solution Overview

This solution implements a comprehensive trading simulator that:

- **Simulates futures trading** with Long and Short positions
- **Supports multiple simultaneous positions** across all three cryptocurrencies
- **Enforces fixed TP/SL percentages** that are symmetric (e.g., +2%/-2%)
- **Applies uniform leverage** (2x, 5x, 10x, or 20x) across all trades
- **Optimizes parameters** using greedy search across TP/SL percentages, leverage levels, and position allocation strategies

## Files

- **`trading_simulator.py`**: Core trading simulator classes
  - `Position`: Represents an open trading position
  - `TradingSimulator`: Handles position management and PnL calculation
  - `OptimalStrategyFinder`: Finds optimal strategy parameters 
  
- **`main.py`**: Main script that processes all days in December 2025
  - Loads data for each day
  - Runs optimization for each day
  - Generates reports and saves results to JSON

- **`requirements.txt`**: Python dependencies (pandas, numpy)

- **`results.json`**: Output file containing detailed results for each day

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the main script to analyze all days in December 2025:

```bash
python main.py
```

The script will:
1. Process each day sequentially
2. Test parameter combinations using greedy optimization
3. Print results for each day
4. Save all results to `results.json`

### Output Format

For each day, the output includes:

- **Final Balance**: Maximum achievable balance
- **Optimal Parameters**: Best TP/SL percentage, leverage, and allocation
- **Target Achievement**: Whether $1,000,000 was reached
- **Number of Trades**: Total trades executed

Detailed trade sequences are saved in `results.json`.

## Algorithm Details

### Core Trading Algorithm

The simulator processes minute-by-minute price data and makes trading decisions based on perfect knowledge of future prices. The algorithm operates in two main phases:

#### Phase 1: Minute-by-Minute Simulation

For each minute of the trading day:

1. **Check Existing Positions**: Evaluate all open positions to see if their Take Profit (TP) or Stop Loss (SL) levels were hit during this minute
   - Long positions: TP is hit if high price >= TP price, SL is hit if low price <= SL price
   - Short positions: TP is hit if low price <= TP price, SL is hit if high price >= SL price
   - Positions close automatically when TP or SL is hit, with PnL calculated and added to balance

2. **Evaluate New Position Opportunities**: For each symbol (BTCUSDT, ETHUSDT, BNBUSDT) where no position is currently open:
   - Calculate available balance (total balance minus margin locked in open positions)
   - If available balance is sufficient, use the direction-finding algorithm to determine if a profitable trade is possible
   - Open a position if TP is guaranteed to hit before SL

#### Phase 2: Direction Finding Algorithm

For a given symbol at a given time, the algorithm determines whether to open a Long or Short position by looking ahead in the price data:

1. **Calculate TP/SL Prices**: Based on the current price and the fixed TP/SL percentage:
   - Long: TP = current_price × (1 + tp_sl_percent/100), SL = current_price × (1 - tp_sl_percent/100)
   - Short: TP = current_price × (1 - tp_sl_percent/100), SL = current_price × (1 + tp_sl_percent/100)

2. **Lookahead Window**: Examine the next 200 minutes of price data (approximately 3.3 hours) to determine price movement potential

3. **Vectorized Analysis**: Use NumPy vectorized operations to efficiently check:
   - For Long: Find the first minute where high >= TP price, and first minute where low <= SL price
   - For Short: Find the first minute where low <= TP price, and first minute where high >= SL price

4. **Decision Logic**:
   - If TP hits before SL (or SL never hits), open a position in that direction
   - If both Long and Short are profitable, choose the direction where TP hits first
   - If neither direction guarantees profit, do not open a position

### Parameter Optimization (Greedy Search)

Instead of testing all possible combinations, the algorithm uses a greedy optimization strategy:

1. **Leverage Priority**: Test leverages from highest to lowest (20x, 10x, 5x, 2x), as higher leverage provides greater profit potential

2. **TP/SL Percentage Search**: For each leverage, test TP/SL percentages in order: 1%, 2%, 3%, 4%, 5%, 6%, 7%, 8%, 9%, 10%, 15%, 20%, 25%, 30%, 50%
   - Smaller percentages allow more frequent trades (positions close faster)
   - Larger percentages allow for bigger price movements but fewer trades

3. **Allocation Testing**: Test position allocations in order: 99%, 95%, 90%, 80%, 70%, 50%
   - Higher allocations maximize capital utilization but reduce available balance for new positions

4. **Early Termination**: 
   - Stop searching when target balance ($1M) is achieved
   - Limit total tests to 100 combinations per day for performance
   - Skip lower leverages if current leverage performs poorly

5. **Refinement Phase**: After finding best leverage and TP/SL percentage, test all allocation levels to optimize position sizing

### Profit Calculation

Profit/Loss for each position is calculated as:

```
PnL = Position Size × Leverage × Price Change Percentage
```

Where:
- **Long positions**: Price Change = (Exit Price - Entry Price) / Entry Price
- **Short positions**: Price Change = (Entry Price - Exit Price) / Entry Price

### Balance Management

- **Available Balance**: Total balance minus sum of all position sizes (margin)
- **Position Size**: Available balance × Allocation percentage
- **Multiple Positions**: Positions can be opened simultaneously across different symbols
- **Position Locking**: Each position locks its margin until it closes

### End-of-Day Handling

Any positions still open at the end of the day are force-closed at the final minute's close price. This ensures a complete daily balance is calculated for optimization purposes.

### Performance Optimizations

1. **Vectorized Operations**: Uses NumPy boolean masks instead of Python loops for direction finding
2. **Limited Lookahead**: Restricts lookahead to 200 minutes instead of scanning entire day
3. **Early Termination**: Stops optimization when target is achieved
4. **Greedy Search**: Tests promising combinations first, limiting total search space

## Results

The solution processes all 31 days in December 2025 and outputs:

1. **Day-by-day analysis** showing maximum achievable profit
2. **Summary statistics** including:
   - Number of days where $1M was achieved
   - Overall maximum balance across all days
   - Optimal parameters for best performance

3. **Detailed trade logs** for each day saved in `results.json` with:
   - Entry and exit prices for each trade
   - Profit/loss per trade
   - Running balance after each trade
   - Timestamps for all trades

## Limitations & Assumptions

- Assumes perfect execution (no slippage)
- No trading fees or funding costs
- Prices execute exactly at TP/SL levels (best-case scenario)
- Minute-level granularity (trades open/close at minute boundaries)
- 200-minute lookahead window (may miss longer-term opportunities)
- Limited to 100 parameter combinations per day (greedy search)

## Performance Considerations

- Greedy optimization tests approximately 100 combinations per day instead of exhaustive search
- Each simulation processes ~1440 minutes of data across 3 symbols
- Processing all 31 days typically completes in reasonable time due to optimizations
- Results are saved incrementally to `results.json` for each day
