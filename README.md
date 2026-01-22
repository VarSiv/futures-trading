# Cryptocurrency Futures Trading Simulator

## Problem Statement

Given perfect knowledge of all future 1-minute price movements for BTCUSDT, ETHUSDT, and BNBUSDT futures within a 24-hour window, determine for each day in December 2025:

- Whether it is possible to grow an initial balance of $10,000 to $1,000,000 under the given trading constraints.
- If so, produce a valid sequence of trades that achieves this.
- Otherwise, estimate the maximum balance achievable under a fixed strategy configuration.

## Scope and Interpretation

This project treats the task as a constrained optimization and simulation problem, not a proof of theoretical global optimality. The goal is to find high-performing, valid strategies under the exact rules provided, using full future price knowledge and realistic execution constraints.

Results should be interpreted as:

- **Best strategies found** under bounded search and fixed parameter assumptions
- **Upper-bound estimates** under a conservative, rule-compliant trading policy

## Trading Constraints Implemented

The simulator strictly enforces the rules from the prompt:

- Long and Short positions are allowed.
- Multiple simultaneous positions are allowed across BTC, ETH, and BNB.
- Each trade is opened with a fixed symmetric TP/SL (+x% / −x%), where x is an integer.
- A single TP/SL percentage and single leverage level are used per simulation.
- **Allowed leverage levels:** 2x, 5x, 10x, 20x.
- Trades cannot be manually closed; they close only when TP or SL is hit.
- No fees, slippage, or funding costs.
- Capital allocation per trade is a fixed fraction of available balance.

## High-Level Approach

The solution consists of a minute-by-minute futures trading simulator combined with a greedy parameter search.

For each day:

1. The simulator replays the full 24-hour price series at 1-minute resolution.
2. At each minute, open positions are checked for TP/SL hits.
3. New positions may be opened if:
   - No position is currently open for that symbol, and
   - Future prices guarantee that the TP level is reached before the SL level.

This ensures all trades are valid, rule-compliant, and non-speculative given perfect foresight.

### Direction Selection (Perfect Foresight Logic)

For a given symbol and minute:

1. TP and SL price levels are computed from the current price and fixed TP/SL percentage.
2. Future highs/lows are scanned within a bounded lookahead window (up to 200 minutes).
3. A trade is opened only if:
   - The TP level is hit before the SL level (or SL is never hit).
   - If both Long and Short satisfy this condition, the direction whose TP is hit sooner is chosen.

This design avoids discretionary exits and respects the "no manual close" constraint.

## Parameter Search Strategy

The simulator does not exhaustively search all possible strategies. Instead, it performs a bounded greedy search:

- **Leverage** tested from highest to lowest: 20x → 2x
- **TP/SL percentages** tested across a predefined discrete set
- **Capital allocation** tested across several fixed fractions

Early stopping when:

- $1,000,000 is reached, or
- Further search is unlikely to outperform the current best result

This keeps runtime reasonable while prioritizing high-upside configurations.

## Output

For each day, the system reports:

- Final balance
- Whether the $1M target was reached
- Best-found TP/SL percentage, leverage, and allocation
- Full trade log with timestamps, prices, PnL, and running balance

All results are saved to `results.json` for inspection and verification.

## Files

- **`trading_simulator.py`**  
  Core simulation logic, trade lifecycle, and strategy evaluation.

- **`main.py`**  
  Runs simulations for all days in December 2025 and aggregates results.

- **`results.json`**  
  Machine-readable output containing per-day summaries and trade sequences.

- **`requirements.txt`**  
  Python dependencies (pandas, numpy)

## Usage

Run the simulation for all days:

```bash
python main.py
```

Test on a single day:

```bash
python test_single_day.py
```

## Assumptions and Limitations

- Execution is idealized (no slippage, fees, or latency).
- Price interaction is limited to minute-level OHLC data.
- Lookahead for trade validation is capped at 200 minutes for performance.
- Open positions at the end of the day are force-closed at the final close price only for evaluation completeness.
- Results represent best found strategies under constrained search, not guaranteed global optima.

## Implementation Details

### Performance Optimizations

1. **Vectorized Operations**: Uses NumPy boolean masks instead of Python loops for direction finding
2. **Bounded Search**: Limits parameter combinations to 250 tests per day
3. **Early Termination**: Stops when target is achieved or further search is unlikely to help

### Results

- Average Final Balance: $836,385.54
- Median Final Balance: $506,701.66
- Maximum Final Balance: $6,242,592.25
- Success Rate: 25.81% (8 out of 31) 