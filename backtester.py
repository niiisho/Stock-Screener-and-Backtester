# backtester.py - Complete with LONG and SHORT positions
import pandas as pd
import numpy as np
from screener import calculate_advanced_indicators
import io


def load_csv_data(csv_file):
    """
    Load OHLC data from user-uploaded CSV
    Required columns: Date, Open, High, Low, Close
    Optional: Volume
    """
    try:
        df = pd.read_csv(io.StringIO(csv_file))
        
        # Required columns
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return None, f"CSV must have columns: {', '.join(required_cols)}. Missing: {', '.join(missing_cols)}"
        
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        # Check if Volume exists
        has_volume = 'Volume' in df.columns
        if not has_volume:
            df['Volume'] = 0  # Placeholder
            print("Volume column not found - Volume and MFI indicators will be skipped")
        
        # Ensure numeric types
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(inplace=True)
        
        if len(df) == 0:
            return None, "CSV contains no valid data"
        
        print(f"CSV loaded: {len(df)} rows from {df.index[0]} to {df.index[-1]}")
        
        return df, None
        
    except Exception as e:
        return None, f"Error: {str(e)}"



def backtest_strategy(data, selected_indicators, params=None):
    if params is None:
        params = {}
    
    initial_capital = float(params.get('initial_capital', 100000))
    risk_per_trade = float(params.get('risk_per_trade', 2.0))
    stop_loss_ticks = float(params.get('stop_loss', 20))
    take_profit_ticks = float(params.get('take_profit', 40))
    tick_size = float(params.get('tick_size', 0.05))
    commission = float(params.get('commission', 20.0))
    slippage_ticks = float(params.get('slippage', 1.0))
    interval = params.get('interval', '1d')
    
    capital = initial_capital
    position = None  # None, 'LONG', or 'SHORT'
    entry_price = 0
    entry_date = None
    stop_loss_price = 0
    take_profit_price = 0
    position_size = 0
    trades = []
    equity_curve = []
    
    print(f"\nStarting backtest...")
    print(f"Data points: {len(data)} | Interval: {interval}")
    
    if len(data) < 60:
        return {'success': False, 'error': 'Need at least 60 candles'}
    
    for i in range(60, len(data)):
        current_date = data.index[i]
        current_high = data['High'].iloc[i]
        current_low = data['Low'].iloc[i]
        current_close = data['Close'].iloc[i]
        
        historical_slice = data.iloc[:i+1]
        ind = calculate_advanced_indicators(historical_slice)
        
        if ind is None:
            continue
        
        # ===== CHECK SL/TP FOR LONG POSITION =====
        if position == 'LONG':
            # Stop Loss hit (price went down)
            if current_low <= stop_loss_price:
                exit_price = stop_loss_price
                profit_amount = (exit_price - entry_price) * position_size - (commission * 2)
                capital += profit_amount
                
                trades.append({
                    'entry_time': str(entry_date),
                    'position': 'long',
                    'entry': round(entry_price, 2),
                    'sl': round(stop_loss_price, 2),
                    'tp': round(take_profit_price, 2),
                    'exit_time': str(current_date),
                    'exit': round(exit_price, 2),
                    'reason': 'SL',
                    'pnl': round(profit_amount, 2),
                    'cumulative_pnl': round(capital - initial_capital, 2)
                })
                
                position = None
                continue
            
            # Take Profit hit (price went up)
            if current_high >= take_profit_price:
                exit_price = take_profit_price
                profit_amount = (exit_price - entry_price) * position_size - (commission * 2)
                capital += profit_amount
                
                trades.append({
                    'entry_time': str(entry_date),
                    'position': 'long',
                    'entry': round(entry_price, 2),
                    'sl': round(stop_loss_price, 2),
                    'tp': round(take_profit_price, 2),
                    'exit_time': str(current_date),
                    'exit': round(exit_price, 2),
                    'reason': 'TP',
                    'pnl': round(profit_amount, 2),
                    'cumulative_pnl': round(capital - initial_capital, 2)
                })
                
                position = None
                continue
        
        # ===== CHECK SL/TP FOR SHORT POSITION =====
        elif position == 'SHORT':
            # Stop Loss hit (price went up)
            if current_high >= stop_loss_price:
                exit_price = stop_loss_price
                profit_amount = (entry_price - exit_price) * position_size - (commission * 2)
                capital += profit_amount
                
                trades.append({
                    'entry_time': str(entry_date),
                    'position': 'short',
                    'entry': round(entry_price, 2),
                    'sl': round(stop_loss_price, 2),
                    'tp': round(take_profit_price, 2),
                    'exit_time': str(current_date),
                    'exit': round(exit_price, 2),
                    'reason': 'SL',
                    'pnl': round(profit_amount, 2),
                    'cumulative_pnl': round(capital - initial_capital, 2)
                })
                
                position = None
                continue
            
            # Take Profit hit (price went down)
            if current_low <= take_profit_price:
                exit_price = take_profit_price
                profit_amount = (entry_price - exit_price) * position_size - (commission * 2)
                capital += profit_amount
                
                trades.append({
                    'entry_time': str(entry_date),
                    'position': 'short',
                    'entry': round(entry_price, 2),
                    'sl': round(stop_loss_price, 2),
                    'tp': round(take_profit_price, 2),
                    'exit_time': str(current_date),
                    'exit': round(exit_price, 2),
                    'reason': 'TP',
                    'pnl': round(profit_amount, 2),
                    'cumulative_pnl': round(capital - initial_capital, 2)
                })
                
                position = None
                continue
        
        # Calculate signals
        buy_signals = 0
        sell_signals = 0
        neutral_signals = 0
        active_count = sum(selected_indicators.values())
        has_volume = data['Volume'].iloc[-1] > 0

        
        if active_count == 0:
            continue
        
        # All 9 indicators
        if selected_indicators.get('rsi', False):
            if ind['rsi'] < 30:
                buy_signals += 1
            elif ind['rsi'] > 70:
                sell_signals += 1
            else:
                neutral_signals += 1
        
        if selected_indicators.get('macd', False):
            if ind['macd'] > ind['macd_signal'] and ind['macd_histogram'] > 0:
                buy_signals += 1
            elif ind['macd'] < ind['macd_signal'] and ind['macd_histogram'] < 0:
                sell_signals += 1
            else:
                neutral_signals += 1
        
        if selected_indicators.get('bollinger', False):
            if current_close < ind['bb_lower']:
                buy_signals += 1
            elif current_close > ind['bb_upper']:
                sell_signals += 1
            else:
                neutral_signals += 1
        
        if selected_indicators.get('stochastic', False):
            if ind['stoch_k'] < 20 and ind['stoch_d'] < 20:
                buy_signals += 1
            elif ind['stoch_k'] > 80 and ind['stoch_d'] > 80:
                sell_signals += 1
            else:
                neutral_signals += 1
        
        if selected_indicators.get('adx', False):
            if ind['adx'] > 25:
                if current_close > ind['sma_20']:
                    buy_signals += 1
                else:
                    sell_signals += 1
            else:
                neutral_signals += 1
        
        if selected_indicators.get('volume', False) and has_volume:
            if ind['volume_ratio'] > 1.5:
                if current_close > ind['sma_20']:
                    buy_signals += 1
                else:
                    sell_signals += 1
            else:
                neutral_signals += 1
        elif selected_indicators.get('volume', False) and not has_volume:
            # Reduce active count since we can't use this indicator
            active_count -= 1        
        
        if selected_indicators.get('cci', False):
            if ind['cci'] < -100:
                buy_signals += 1
            elif ind['cci'] > 100:
                sell_signals += 1
            else:
                neutral_signals += 1
        
        if selected_indicators.get('willr', False):
            if ind['willr'] < -80:
                buy_signals += 1
            elif ind['willr'] > -20:
                sell_signals += 1
            else:
                neutral_signals += 1
        
        if selected_indicators.get('mfi', False) and has_volume:
            if ind['mfi'] < 20:
                buy_signals += 1
            elif ind['mfi'] > 80:
                sell_signals += 1
            else:
                neutral_signals += 1
        elif selected_indicators.get('mfi', False) and not has_volume:
            # Reduce active count since we can't use this indicator
            active_count -= 1

        # Recalculate if active_count changed
        if active_count == 0:
            continue        
        
        # Determine signal based on majority
        if buy_signals > sell_signals and buy_signals > neutral_signals:
            signal = 'BUY'
        elif sell_signals > buy_signals and sell_signals > neutral_signals:
            signal = 'SELL'
        else:
            signal = 'NEUTRAL'
        
        # ===== ENTRY LOGIC - OPEN NEW POSITION =====
        if position is None:
            # BUY Signal - Enter LONG
            if signal == 'BUY':
                entry_price = current_close + (slippage_ticks * tick_size)
                stop_loss_price = entry_price - (stop_loss_ticks * tick_size)
                take_profit_price = entry_price + (take_profit_ticks * tick_size)
                
                risk_amount = capital * (risk_per_trade / 100)
                risk_per_share = entry_price - stop_loss_price
                
                if risk_per_share > 0:
                    position_size = int(risk_amount / risk_per_share)
                else:
                    position_size = int((capital * 0.1) / entry_price)
                
                if position_size > 0:
                    position = 'LONG'
                    entry_date = current_date
                    print(f"LONG: {current_date} | Entry: {entry_price:.2f} | SL: {stop_loss_price:.2f} | TP: {take_profit_price:.2f}")
            
            # SELL Signal - Enter SHORT
            elif signal == 'SELL':
                entry_price = current_close - (slippage_ticks * tick_size)
                stop_loss_price = entry_price + (stop_loss_ticks * tick_size)
                take_profit_price = entry_price - (take_profit_ticks * tick_size)
                
                risk_amount = capital * (risk_per_trade / 100)
                risk_per_share = stop_loss_price - entry_price
                
                if risk_per_share > 0:
                    position_size = int(risk_amount / risk_per_share)
                else:
                    position_size = int((capital * 0.1) / entry_price)
                
                if position_size > 0:
                    position = 'SHORT'
                    entry_date = current_date
                    print(f"SHORT: {current_date} | Entry: {entry_price:.2f} | SL: {stop_loss_price:.2f} | TP: {take_profit_price:.2f}")
        
        # ===== EXIT LOGIC - CLOSE EXISTING POSITION =====
        elif position == 'LONG' and signal == 'SELL':
            # Exit LONG on SELL signal
            exit_price = current_close - (slippage_ticks * tick_size)
            profit_amount = (exit_price - entry_price) * position_size - (commission * 2)
            capital += profit_amount
            
            trades.append({
                'entry_time': str(entry_date),
                'position': 'long',
                'entry': round(entry_price, 2),
                'sl': round(stop_loss_price, 2),
                'tp': round(take_profit_price, 2),
                'exit_time': str(current_date),
                'exit': round(exit_price, 2),
                'reason': 'Signal',
                'pnl': round(profit_amount, 2),
                'cumulative_pnl': round(capital - initial_capital, 2)
            })
            
            position = None
            print(f"EXIT LONG: {current_date} | Exit: {exit_price:.2f} | P&L: {profit_amount:.2f}")
        
        elif position == 'SHORT' and signal == 'BUY':
            # Exit SHORT on BUY signal
            exit_price = current_close + (slippage_ticks * tick_size)
            profit_amount = (entry_price - exit_price) * position_size - (commission * 2)
            capital += profit_amount
            
            trades.append({
                'entry_time': str(entry_date),
                'position': 'short',
                'entry': round(entry_price, 2),
                'sl': round(stop_loss_price, 2),
                'tp': round(take_profit_price, 2),
                'exit_time': str(current_date),
                'exit': round(exit_price, 2),
                'reason': 'Signal',
                'pnl': round(profit_amount, 2),
                'cumulative_pnl': round(capital - initial_capital, 2)
            })
            
            position = None
            print(f"EXIT SHORT: {current_date} | Exit: {exit_price:.2f} | P&L: {profit_amount:.2f}")
        
        # Track equity curve
        current_equity = capital
        if position == 'LONG':
            current_equity = capital + ((current_close - entry_price) * position_size)
        elif position == 'SHORT':
            current_equity = capital + ((entry_price - current_close) * position_size)
        
        equity_curve.append({
            'date': str(current_date),
            'equity': round(current_equity, 2)
        })
    
    # Calculate metrics
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t['pnl'] > 0])
    losing_trades = total_trades - winning_trades
    
    total_return = ((capital - initial_capital) / initial_capital) * 100
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    if total_trades > 0:
        avg_profit = sum([t['pnl'] for t in trades]) / total_trades
        avg_win = sum([t['pnl'] for t in trades if t['pnl'] > 0]) / winning_trades if winning_trades > 0 else 0
        avg_loss = sum([t['pnl'] for t in trades if t['pnl'] < 0]) / losing_trades if losing_trades > 0 else 0
        sl_exits = len([t for t in trades if t['reason'] == 'SL'])
        tp_exits = len([t for t in trades if t['reason'] == 'TP'])
        signal_exits = len([t for t in trades if t['reason'] == 'Signal'])
    else:
        avg_profit = avg_win = avg_loss = 0
        sl_exits = tp_exits = signal_exits = 0
    
    equity_values = [e['equity'] for e in equity_curve]
    peak = equity_values[0] if equity_values else initial_capital
    max_dd = 0
    
    for value in equity_values:
        if value > peak:
            peak = value
        dd = ((peak - value) / peak) * 100
        if dd > max_dd:
            max_dd = dd
    
    print(f"\nBacktest Complete!")
    print(f"Total Trades: {total_trades} | Win Rate: {win_rate:.1f}%")
    print(f"Long Trades: {len([t for t in trades if t['position'] == 'long'])}")
    print(f"Short Trades: {len([t for t in trades if t['position'] == 'short'])}")
    
    return {
        'success': True,
        'initial_capital': round(initial_capital, 2),
        'final_capital': round(capital, 2),
        'total_return': round(total_return, 2),
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': round(win_rate, 2),
        'avg_profit_per_trade': round(avg_profit, 2),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'max_drawdown': round(max_dd, 2),
        'sl_exits': sl_exits,
        'tp_exits': tp_exits,
        'signal_exits': signal_exits,
        'equity_curve': equity_curve[-50:],
        'trades': trades
    }
