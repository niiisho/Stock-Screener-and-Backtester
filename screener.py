# screener.py - FINAL VERSION with 9 Indicators
import yfinance as yf
import pandas as pd
import numpy as np
import talib as ta


def get_stock_data(symbol, period='6mo', interval='1d'):
    """
    Get stock data for Indian stocks with interval support
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
        period: '1d', '5d', '7d', '1mo', '3mo', '6mo', '1y', '2y', '5y'
        interval: '1m', '5m', '15m', '30m', '60m', '1h', '1d'
    
    Returns:
        DataFrame with OHLC data or None if error
    """
    try:
        # Add .NS suffix for NSE stocks
        if not symbol.endswith('.NS'):
            symbol = symbol + '.NS'
        
        print(f"\nFetching data: {symbol}")
        print(f"   Period: {period} | Interval: {interval}")
        
        stock = yf.Ticker(symbol)
        
        # Fetch data with interval parameter
        data = stock.history(period=period, interval=interval)
        
        if data.empty:
            print(f"No data returned for {symbol}")
            return None
        
        print(f"Fetched {len(data)} candles from {data.index[0]} to {data.index[-1]}")
        
        return data
        
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def calculate_advanced_indicators(data):
    """
    Calculate multiple technical indicators using TA-Lib
    Returns: Dictionary with all indicator values
    """
    # Convert to float64 (TA-Lib requirement)
    close = np.array(data['Close'].values, dtype=np.float64)
    high = np.array(data['High'].values, dtype=np.float64)
    low = np.array(data['Low'].values, dtype=np.float64)
    volume = np.array(data['Volume'].values, dtype=np.float64)
    
    indicators = {}
    
    try:
        # RSI (Relative Strength Index)
        indicators['rsi'] = ta.RSI(close, timeperiod=14)[-1]
        
        # MACD (Moving Average Convergence Divergence)
        macd, signal, hist = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        indicators['macd'] = macd[-1]
        indicators['macd_signal'] = signal[-1]
        indicators['macd_histogram'] = hist[-1]
        
        # Bollinger Bands
        upper, middle, lower = ta.BBANDS(close, timeperiod=20)
        indicators['bb_upper'] = upper[-1]
        indicators['bb_middle'] = middle[-1]
        indicators['bb_lower'] = lower[-1]
        
        # Moving Averages
        indicators['sma_20'] = ta.SMA(close, timeperiod=20)[-1]
        indicators['sma_50'] = ta.SMA(close, timeperiod=50)[-1]
        indicators['ema_12'] = ta.EMA(close, timeperiod=12)[-1]
        indicators['ema_26'] = ta.EMA(close, timeperiod=26)[-1]
        
        # Stochastic Oscillator
        slowk, slowd = ta.STOCH(high, low, close)
        indicators['stoch_k'] = slowk[-1]
        indicators['stoch_d'] = slowd[-1]
        
        # ADX (Trend Strength)
        indicators['adx'] = ta.ADX(high, low, close, timeperiod=14)[-1]
        
        # CCI (Commodity Channel Index)
        indicators['cci'] = ta.CCI(high, low, close, timeperiod=14)[-1]
        
        # Williams %R
        indicators['willr'] = ta.WILLR(high, low, close, timeperiod=14)[-1]
        
        # MFI (Money Flow Index)
        indicators['mfi'] = ta.MFI(high, low, close, volume, timeperiod=14)[-1]
        
        # Volume indicators
        indicators['avg_volume'] = np.mean(volume[-20:])
        indicators['current_volume'] = volume[-1]
        indicators['volume_ratio'] = volume[-1] / np.mean(volume[-20:])
        
        # ATR (Average True Range - Volatility)
        indicators['atr'] = ta.ATR(high, low, close, timeperiod=14)[-1]
        
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return None
    
    return indicators


def generate_advanced_signal(symbol, selected_indicators=None, data=None):
    """
    Generate trading signal based on majority vote from selected indicators
    Returns: BUY, SELL, or HOLD
    """
    if data is None:
        data = get_stock_data(symbol)
    
    if data is None or len(data) < 60:
        return None
    
    # Default to all indicators if none selected
    if selected_indicators is None:
        selected_indicators = {
            'rsi': True, 'macd': True, 'bollinger': True,
            'stochastic': True, 'adx': True, 'volume': True,
            'cci': True, 'willr': True, 'mfi': True
        }
    
    # Count active indicators
    active_count = sum(selected_indicators.values())
    if active_count == 0:
        return None
    
    # Calculate indicators
    indicators = calculate_advanced_indicators(data)
    if indicators is None:
        return None
    
    current_price = data['Close'].iloc[-1]
    
    # Count signals
    buy_signals = 0
    sell_signals = 0
    neutral_signals = 0
    
    # 1. RSI
    if selected_indicators.get('rsi', False):
        if indicators['rsi'] < 30:
            buy_signals += 1
        elif indicators['rsi'] > 70:
            sell_signals += 1
        else:
            neutral_signals += 1
    
    # 2. MACD
    if selected_indicators.get('macd', False):
        if indicators['macd'] > indicators['macd_signal'] and indicators['macd_histogram'] > 0:
            buy_signals += 1
        elif indicators['macd'] < indicators['macd_signal'] and indicators['macd_histogram'] < 0:
            sell_signals += 1
        else:
            neutral_signals += 1
    
    # 3. Bollinger Bands
    if selected_indicators.get('bollinger', False):
        if current_price < indicators['bb_lower']:
            buy_signals += 1
        elif current_price > indicators['bb_upper']:
            sell_signals += 1
        else:
            neutral_signals += 1
    
    # 4. Stochastic
    if selected_indicators.get('stochastic', False):
        if indicators['stoch_k'] < 20 and indicators['stoch_d'] < 20:
            buy_signals += 1
        elif indicators['stoch_k'] > 80 and indicators['stoch_d'] > 80:
            sell_signals += 1
        else:
            neutral_signals += 1
    
    # 5. ADX (Trend Strength)
    if selected_indicators.get('adx', False):
        if indicators['adx'] > 25:
            if current_price > indicators['sma_20']:
                buy_signals += 1
            else:
                sell_signals += 1
        else:
            neutral_signals += 1
    
    # 6. Volume
    if selected_indicators.get('volume', False):
        if indicators['volume_ratio'] > 1.5:
            if current_price > indicators['sma_20']:
                buy_signals += 1
            else:
                sell_signals += 1
        else:
            neutral_signals += 1
    
    # 7. CCI
    if selected_indicators.get('cci', False):
        if indicators['cci'] < -100:
            buy_signals += 1
        elif indicators['cci'] > 100:
            sell_signals += 1
        else:
            neutral_signals += 1
    
    # 8. Williams %R
    if selected_indicators.get('willr', False):
        if indicators['willr'] < -80:
            buy_signals += 1
        elif indicators['willr'] > -20:
            sell_signals += 1
        else:
            neutral_signals += 1
    
    # 9. MFI (Money Flow Index)
    if selected_indicators.get('mfi', False):
        if indicators['mfi'] < 20:
            buy_signals += 1
        elif indicators['mfi'] > 80:
            sell_signals += 1
        else:
            neutral_signals += 1
    
    # Calculate percentages
    buy_percentage = (buy_signals / active_count) * 100
    sell_percentage = (sell_signals / active_count) * 100
    neutral_percentage = (neutral_signals / active_count) * 100
    
    # Determine signal based on majority vote
    if buy_signals > sell_signals and buy_signals >= neutral_signals:
        signal = 'BUY'
    elif sell_signals > buy_signals and sell_signals >= neutral_signals:
        signal = 'SELL'
    else:
        signal = 'HOLD'
    
    # Calculate confidence (how strong is the majority)
    max_signals = max(buy_signals, sell_signals, neutral_signals)
    confidence = (max_signals / active_count) * 100
    
    # Risk assessment
    risk_factors = 0
    if indicators['rsi'] > 80 or indicators['rsi'] < 20:
        risk_factors += 1
    if indicators['adx'] < 20:
        risk_factors += 1
    if indicators['volume_ratio'] < 0.5:
        risk_factors += 1
    
    risk_score = (risk_factors / 3) * 100
    
    return {
        'symbol': symbol,
        'signal': signal,
        'confidence': round(confidence, 1),
        'price': round(current_price, 2),
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'neutral_signals': neutral_signals,
        'buy_percentage': round(buy_percentage, 1),
        'sell_percentage': round(sell_percentage, 1),
        'neutral_percentage': round(neutral_percentage, 1),
        'risk_score': round(risk_score, 1),
        'rsi': round(indicators['rsi'], 2),
        'macd': round(indicators['macd'], 2),
        'adx': round(indicators['adx'], 2),
        'cci': round(indicators['cci'], 2),
        'willr': round(indicators['willr'], 2),
        'mfi': round(indicators['mfi'], 2),
        'volume_ratio': round(indicators['volume_ratio'], 2)
    }



def screen_multiple_stocks(stocks, selected_indicators, timeframe='1d'):
    """
    Screen multiple stocks with selected indicators and timeframe
    
    Args:
        stocks: List of stock symbols
        selected_indicators: Dict of which indicators to use
        timeframe: '1d', '1h', '30m', '15m', etc.
    
    Returns:
        List of results
    """
    results = []
    
    # Determine period based on timeframe
    period_map = {
        '1m': '7d',
        '5m': '60d',
        '15m': '60d',
        '30m': '60d',
        '1h': '60d',
        '1d': '6mo'
    }
    period = period_map.get(timeframe, '6mo')
    
    print(f"\nScreening {len(stocks)} stocks with timeframe: {timeframe}, period: {period}")
    
    for symbol in stocks:
        print(f"\nAnalyzing {symbol}...")
        
        # Get data with timeframe
        data = get_stock_data(symbol, period=period, interval=timeframe)
        
        if data is None or len(data) < 60:
            print(f"Skipping {symbol} - insufficient data")
            continue
        
        # Generate signal
        signal_data = generate_advanced_signal(symbol, selected_indicators, data=data)
        
        if signal_data:
            results.append(signal_data)
    
    # Sort by signal priority
    signal_priority = {
        'STRONG BUY': 5,
        'BUY': 4,
        'STRONG SELL': 3,
        'SELL': 2,
        'HOLD': 1
    }
    
    results.sort(key=lambda x: (signal_priority.get(x['signal'], 0), x.get('buy_percentage', 0)), reverse=True)
    
    return results



def display_results(results):
    """
    Display screening results in terminal
    """
    print("\n" + "="*100)
    print("STOCK SCREENING RESULTS")
    print("="*100)
    
    for i, stock in enumerate(results, 1):
        signal_emoji = {
            'STRONG BUY': '🟢🟢',
            'BUY': '🟢',
            'HOLD': '🟡',
            'SELL': '🔴',
            'STRONG SELL': '🔴🔴'
        }
        
        print(f"\n{i}. {signal_emoji.get(stock['signal'], '⚪')} {stock['symbol']}")
        print(f"   Signal: {stock['signal']} ({stock['confidence']} confidence)")
        print(f"   Price: ₹{stock['price']} | Risk: {stock['risk_score']}/100")
        print(f"   Agreement: {stock['buy_signals']} buy, {stock['sell_signals']} sell, {stock['neutral_signals']} neutral")
        print(f"   Buy: {stock['buy_percentage']}% | Sell: {stock['sell_percentage']}%")
        print(f"   Reasons: {', '.join(stock['reasons'])}")
    
    print("\n" + "="*100)


# Test when run directly
if __name__ == "__main__":
    indian_stocks = [
        'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK',
        'BAJFINANCE', 'TATAMOTORS', 'WIPRO', 'SUNPHARMA', 'MARUTI',
        'BHARTIARTL', 'KOTAKBANK', 'LT', 'AXISBANK', 'ITC'
    ]
    
    # Test with all indicators
    print("=" * 100)
    print("TEST 1: ALL 9 INDICATORS")
    print("=" * 100)
    results = screen_multiple_stocks(indian_stocks)
    display_results(results)
    
    # Test with only 3 new indicators
    print("\n\n" + "=" * 100)
    print("TEST 2: ONLY NEW INDICATORS (CCI + Williams %R + MFI)")
    print("=" * 100)
    custom_indicators = {
        'rsi': False,
        'macd': False,
        'bollinger': False,
        'stochastic': False,
        'adx': False,
        'volume': False,
        'cci': True,
        'willr': True,
        'mfi': True
    }
    results2 = screen_multiple_stocks(indian_stocks[:5], custom_indicators)
    display_results(results2)
