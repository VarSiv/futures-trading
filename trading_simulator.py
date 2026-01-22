"""
trading simulator for cryptocurrency futures trading
determines maximum profit achievable with fixed tp/sl and leverage
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import os


class TradeType(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Position:
    symbol: str
    trade_type: TradeType
    entry_price: float
    size: float
    leverage: int
    tp_price: float
    sl_price: float
    entry_time: int
    
    def check_tp_sl(self, high: float, low: float) -> Optional[float]:
        """check if tp or sl is hit, return exit price if hit"""
        if self.trade_type == TradeType.LONG:
            if high >= self.tp_price:
                return self.tp_price
            if low <= self.sl_price:
                return self.sl_price
        else:
            if low <= self.tp_price:
                return self.tp_price
            if high >= self.sl_price:
                return self.sl_price
        return None
    
    def calculate_pnl(self, exit_price: float) -> float:
        if self.trade_type == TradeType.LONG:
            pct_change = (exit_price - self.entry_price) / self.entry_price
        else:
            pct_change = (self.entry_price - exit_price) / self.entry_price
        return self.size * self.leverage * pct_change


class TradingSimulator:
    def __init__(
        self,
        initial_balance: float = 10000.0,
        tp_sl_percent: int = 2,
        leverage: int = 20,
        position_allocation: float = 0.9
    ):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.tp_sl_percent = tp_sl_percent
        self.leverage = leverage
        self.position_allocation = position_allocation
        
        self.positions: List[Position] = []
        self.closed_trades: List[Dict] = []
        self.symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        
    def reset(self):
        self.balance = self.initial_balance
        self.positions = []
        self.closed_trades = []
    
    def open_position(
        self,
        symbol: str,
        trade_type: TradeType,
        current_price: float,
        timestamp: int
    ) -> bool:
        position_size = self.balance * self.position_allocation
        
        if position_size < 1.0:
            return False
        if trade_type == TradeType.LONG:
            tp_price = current_price * (1 + self.tp_sl_percent / 100.0)
            sl_price = current_price * (1 - self.tp_sl_percent / 100.0)
        else:
            tp_price = current_price * (1 - self.tp_sl_percent / 100.0)
            sl_price = current_price * (1 + self.tp_sl_percent / 100.0)
        
        position = Position(
            symbol=symbol,
            trade_type=trade_type,
            entry_price=current_price,
            size=position_size,
            leverage=self.leverage,
            tp_price=tp_price,
            sl_price=sl_price,
            entry_time=timestamp
        )
        
        self.positions.append(position)
        return True
    
    def process_minute(self, minute_data: Dict[str, Dict]) -> List[Dict]:
        closed_this_minute = []
        positions_to_close = []
        for pos in self.positions:
            if pos.symbol in minute_data:
                data = minute_data[pos.symbol]
                exit_price = pos.check_tp_sl(data['high'], data['low'])
                
                if exit_price is not None:
                    pnl = pos.calculate_pnl(exit_price)
                    self.balance += pnl
                    
                    closed_trade = {
                        'symbol': pos.symbol,
                        'type': pos.trade_type.value,
                        'entry_price': pos.entry_price,
                        'exit_price': exit_price,
                        'size': pos.size,
                        'pnl': pnl,
                        'entry_time': pos.entry_time,
                        'exit_time': data['timestamp'],
                        'balance_after': self.balance
                    }
                    closed_this_minute.append(closed_trade)
                    self.closed_trades.append(closed_trade)
                    positions_to_close.append(pos)
        
        for pos in positions_to_close:
            self.positions.remove(pos)
        
        return closed_this_minute
    
    def get_available_balance(self) -> float:
        locked = sum(pos.size for pos in self.positions)
        available = self.balance - locked
        return max(0.0, available)


class OptimalStrategyFinder:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.allowed_leverages = [2, 5, 10, 20]
        self.allowed_tp_sl_percents = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 50]
        self.allowed_allocations = [0.5, 0.7, 0.8, 0.9, 0.95, 0.99]
        
    def load_day_data(self, date_str: str) -> Dict[str, pd.DataFrame]:
        data = {}
        for symbol in ["btc", "eth", "bnb"]:
            filepath = os.path.join(self.data_dir, symbol, f"{symbol.upper()}USDT-1m-{date_str}.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                df['timestamp'] = pd.to_datetime(df['open_time'], unit='ms')
                data[symbol.upper() + "USDT"] = df
        return data
    
    def find_best_direction(
        self, 
        df: pd.DataFrame, 
        start_idx: int, 
        tp_sl_percent: float,
        lookahead: int = None
    ) -> Optional[Tuple[TradeType, float]]:
        if start_idx >= len(df) - 1:
            return None
        
        max_lookahead = 200
        if lookahead is None:
            lookahead = min(max_lookahead, len(df) - start_idx - 1)
        else:
            lookahead = min(lookahead, max_lookahead, len(df) - start_idx - 1)
        
        if lookahead <= 0:
            return None
        
        current_price = df.iloc[start_idx]['close']
        tp_price_long = current_price * (1 + tp_sl_percent / 100.0)
        sl_price_long = current_price * (1 - tp_sl_percent / 100.0)
        tp_price_short = current_price * (1 - tp_sl_percent / 100.0)
        sl_price_short = current_price * (1 + tp_sl_percent / 100.0)
        
        start_slice = start_idx + 1
        end_slice = min(start_idx + 1 + lookahead, len(df))
        future_highs = df.iloc[start_slice:end_slice]['high'].values
        future_lows = df.iloc[start_slice:end_slice]['low'].values
        
        long_tp_idx = None
        long_sl_idx = None
        tp_mask = future_highs >= tp_price_long
        sl_mask = future_lows <= sl_price_long
        
        if tp_mask.any():
            long_tp_idx = np.argmax(tp_mask)
        if sl_mask.any():
            long_sl_idx = np.argmax(sl_mask)
        
        short_tp_idx = None
        short_sl_idx = None
        tp_mask_short = future_lows <= tp_price_short
        sl_mask_short = future_highs >= sl_price_short
        
        if tp_mask_short.any():
            short_tp_idx = np.argmax(tp_mask_short)
        if sl_mask_short.any():
            short_sl_idx = np.argmax(sl_mask_short)
        
        long_good = long_tp_idx is not None and (long_sl_idx is None or long_tp_idx < long_sl_idx)
        short_good = short_tp_idx is not None and (short_sl_idx is None or short_tp_idx < short_sl_idx)
        
        if long_good and short_good:
            if long_tp_idx < short_tp_idx:
                return (TradeType.LONG, 1.0)
            else:
                return (TradeType.SHORT, 1.0)
        elif long_good:
            return (TradeType.LONG, 1.0)
        elif short_good:
            return (TradeType.SHORT, 1.0)
        
        return None
    
    def simulate_day(
        self,
        date_str: str,
        tp_sl_percent: int,
        leverage: int,
        position_allocation: float = 0.95
    ) -> Tuple[float, List[Dict]]:
        symbol_data = self.load_day_data(date_str)
        if not symbol_data:
            return 10000.0, []
        
        simulator = TradingSimulator(
            initial_balance=10000.0,
            tp_sl_percent=tp_sl_percent,
            leverage=leverage,
            position_allocation=position_allocation
        )
        
        all_timestamps = set()
        for df in symbol_data.values():
            all_timestamps.update(df['open_time'].values)
        all_timestamps = sorted(all_timestamps)
        
        symbol_indices = {}
        for symbol, df in symbol_data.items():
            symbol_indices[symbol] = {ts: idx for idx, ts in enumerate(df['open_time'].values)}
        
        total_minutes = len(all_timestamps)
        for minute_idx, timestamp in enumerate(all_timestamps):
            minute_data = {}
            for symbol, df in symbol_data.items():
                if timestamp in symbol_indices[symbol]:
                    idx = symbol_indices[symbol][timestamp]
                    row = df.iloc[idx]
                    minute_data[symbol] = {
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'timestamp': timestamp,
                        'index': idx
                    }
            
            # Process any TP/SL hits first
            simulator.process_minute(minute_data)
            
            # Progress indicator for long-running simulations (less frequent)
            if minute_idx > 0 and minute_idx % 500 == 0:
                pass  # Removed verbose progress to speed up
            
            # Try to open new positions on each symbol
            # Process symbols in order, updating available balance as we go
            for symbol, data in minute_data.items():
                # Skip if we already have a position in this symbol
                if any(pos.symbol == symbol for pos in simulator.positions):
                    continue
                
                # Check available balance
                available_balance = simulator.get_available_balance()
                if available_balance < 50:  # Minimum position size threshold
                    continue
                
                # Find best direction for this symbol at this time
                df = symbol_data[symbol]
                # Use default lookahead (limited to 200 minutes for performance)
                direction_result = self.find_best_direction(
                    df, 
                    data['index'], 
                    tp_sl_percent
                )
                
                if direction_result:
                    direction, _ = direction_result
                    simulator.open_position(
                        symbol=symbol,
                        trade_type=direction,
                        current_price=data['close'],
                        timestamp=timestamp
                    )
        
        if simulator.positions:
            last_timestamp = all_timestamps[-1]
            last_minute_data = {}
            for symbol, df in symbol_data.items():
                if last_timestamp in symbol_indices[symbol]:
                    idx = symbol_indices[symbol][last_timestamp]
                    row = df.iloc[idx]
                    last_minute_data[symbol] = {
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'timestamp': last_timestamp
                    }
            
            for pos in list(simulator.positions):
                if pos.symbol in last_minute_data:
                    exit_price = last_minute_data[pos.symbol]['close']
                    pnl = pos.calculate_pnl(exit_price)
                    simulator.balance += pnl
                    
                    closed_trade = {
                        'symbol': pos.symbol,
                        'type': pos.trade_type.value,
                        'entry_price': pos.entry_price,
                        'exit_price': exit_price,
                        'size': pos.size,
                        'pnl': pnl,
                        'entry_time': pos.entry_time,
                        'exit_time': last_timestamp,
                        'balance_after': simulator.balance
                    }
                    simulator.closed_trades.append(closed_trade)
                    simulator.positions.remove(pos)
        
        return simulator.balance, simulator.closed_trades
    
    def find_optimal_strategy(
        self,
        date_str: str,
        target_balance: float = 1000000.0
    ) -> Dict:
        best_result = {
            'final_balance': 10000.0,
            'tp_sl_percent': None,
            'leverage': None,
            'position_allocation': None,
            'trades': [],
            'achieved_target': False
        }
        
        leverages = sorted(self.allowed_leverages, reverse=True)
        tp_sl_percents = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 50]
        allocations = [0.99, 0.95, 0.9, 0.8, 0.7, 0.5]
        
        tested = 0
        max_tests = 100
        
        for leverage in leverages:
            if tested >= max_tests:
                break
                
            best_tp_sl = None
            best_balance_for_leverage = 10000.0
            
            for tp_sl_percent in tp_sl_percents:
                if tested >= max_tests:
                    break
                    
                for allocation in allocations[:2]:
                    tested += 1
                    
                    try:
                        final_balance, trades = self.simulate_day(
                            date_str,
                            tp_sl_percent,
                            leverage,
                            allocation
                        )
                        
                        if final_balance > best_result['final_balance']:
                            best_result['final_balance'] = final_balance
                            best_result['tp_sl_percent'] = tp_sl_percent
                            best_result['leverage'] = leverage
                            best_result['position_allocation'] = allocation
                            best_result['trades'] = trades
                            best_result['achieved_target'] = final_balance >= target_balance
                            
                            if best_result['achieved_target']:
                                print(f"  Target achieved after {tested} tests!")
                                return best_result
                        
                        # Track best for this leverage
                        if final_balance > best_balance_for_leverage:
                            best_balance_for_leverage = final_balance
                            best_tp_sl = tp_sl_percent
                    except Exception:
                        continue
            
            if best_balance_for_leverage < best_result['final_balance'] * 0.5:
                break
        
        if best_result['tp_sl_percent'] and best_result['leverage']:
            print(f"  Refining allocation for best parameters...", end='\r')
            for allocation in allocations:
                if allocation == best_result['position_allocation']:
                    continue
                tested += 1
                try:
                    final_balance, trades = self.simulate_day(
                        date_str,
                        best_result['tp_sl_percent'],
                        best_result['leverage'],
                        allocation
                    )
                    
                    if final_balance > best_result['final_balance']:
                        best_result['final_balance'] = final_balance
                        best_result['position_allocation'] = allocation
                        best_result['trades'] = trades
                        best_result['achieved_target'] = final_balance >= target_balance
                        
                        if best_result['achieved_target']:
                            break
                except Exception:
                    continue
        
        print(f"  Completed {tested} tests (greedy optimization).")
        return best_result


if __name__ == "__main__":
    finder = OptimalStrategyFinder()
    result = finder.find_optimal_strategy("2025-12-01")
    print(f"Best result: ${result['final_balance']:,.2f}")
    print(f"Parameters: {result['tp_sl_percent']}% TP/SL, {result['leverage']}x leverage")

