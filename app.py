# app.py - Updated screen endpoint
from flask import Flask, render_template, jsonify, request, Response
from screener import screen_multiple_stocks, generate_advanced_signal
import pandas as pd
from backtester import backtest_strategy, load_csv_data
from strategy import current_strategy
import json
import io

app = Flask(__name__)

# Popular Indian stocks
DEFAULT_STOCKS = [
    'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK',
    'BAJFINANCE', 'WIPRO', 'SUNPHARMA', 'MARUTI',
    'BHARTIARTL', 'KOTAKBANK', 'LT', 'AXISBANK', 'ITC'
]

@app.route('/')
def home():
    """Render main dashboard"""
    return render_template('index.html')

@app.route('/api/screen', methods=['POST'])
def screen_stocks():
    """
    Screen stocks with selected indicators and timeframe
    """
    try:
        data = request.get_json()
        stocks = data.get('stocks', DEFAULT_STOCKS)
        selected_indicators = data.get('indicators', {})
        timeframe = data.get('timeframe', '1d')  # NEW
        
        print(f"\nAPI Request received:")
        print(f"Stocks: {stocks}")
        print(f"Timeframe: {timeframe}")
        print(f"Selected Indicators: {selected_indicators}")
        
        results = screen_multiple_stocks(stocks, selected_indicators, timeframe)
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': str(pd.Timestamp.now()),
            'indicators_used': selected_indicators,
            'timeframe': timeframe
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    

@app.route('/api/export-csv', methods=['POST'])
def export_csv():
    """
    Export screening results to CSV
    """
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No results to export'
            }), 400
        
        # Convert results to pandas DataFrame
        df = pd.DataFrame(results)
        
        # Select and reorder columns for CSV
        columns_to_export = [
            'symbol', 'signal', 'confidence', 'price', 
            'buy_percentage', 'sell_percentage',
            'buy_signals', 'sell_signals', 'neutral_signals',
            'risk_score', 'rsi', 'macd', 'adx', 
            'cci', 'willr', 'mfi', 'volume_ratio'
        ]
        
        # Keep only columns that exist
        columns_to_export = [col for col in columns_to_export if col in df.columns]
        df_export = df[columns_to_export]
        
        # Rename columns for better readability
        df_export.columns = [
            'Stock', 'Signal', 'Confidence', 'Price (₹)',
            'Buy %', 'Sell %',
            'Buy Signals', 'Sell Signals', 'Neutral Signals',
            'Risk Score', 'RSI', 'MACD', 'ADX',
            'CCI', 'Williams %R', 'MFI', 'Volume Ratio'
        ]
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        # Create response with CSV file
        response = Response(
            csv_data,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=stock_screening_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
        
        return response
        
    except Exception as e:
        print(f"Error exporting CSV: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/update-strategy', methods=['POST'])
def update_strategy():
    """
    Update global strategy configuration
    Used by all modes (screener, backtester)
    """
    try:
        data = request.get_json()
        indicators = data.get('indicators', {})
        
        current_strategy.set_indicators(indicators)
        
        return jsonify({
            'success': True,
            'strategy': current_strategy.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/backtest', methods=['POST'])
def backtest():
    """
    Run backtest with timeframe selection and validation
    """
    try:
        data = request.get_json()
        
        # Get parameters
        csv_data = data.get('csv_data', None)
        stock_symbol = data.get('stock', 'RELIANCE')
        period = data.get('period', '6mo')
        interval = data.get('interval', '1d')
        params = data.get('params', {})
        
        print(f"\nBacktest Request:")
        print(f"   Stock: {stock_symbol}")
        print(f"   Period: {period}")
        print(f"   Interval: {interval}")
        
        if csv_data:
            # User uploaded CSV
            from backtester import load_csv_data
            df, error = load_csv_data(csv_data)
            if error:
                return jsonify({'success': False, 'error': error}), 400
        else:
            # Auto-fetch data - IMPORTANT: Pass interval parameter
            from screener import get_stock_data
            df = get_stock_data(stock_symbol, period=period, interval=interval)

            # In app.py, after fetching data, add:
            if df is not None:
                print(f"\nData fetched successfully:")
                print(f"   Rows: {len(df)}")
                print(f"   Columns: {list(df.columns)}")
                print(f"   First date: {df.index[0]}")
                print(f"   Last date: {df.index[-1]}")
                print(f"   First 3 rows:")
                print(df.head(3))

            
            if df is None or df.empty:
                return jsonify({
                    'success': False, 
                    'error': f'Could not fetch data for {stock_symbol}. Try a different stock or timeframe.'
                }), 400
            
            if len(df) < 60:
                return jsonify({
                    'success': False,
                    'error': f'Not enough data points ({len(df)}). Need at least 60 candles for indicators. Try a longer period.'
                }), 400

        
        results = backtest_strategy(df, current_strategy.selected_indicators, params)
        return jsonify(results)
    
    except Exception as e:
        import traceback
        print(f"Backtest error: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500



def validate_timeframe(interval, period):
    """
    Validate interval + period combination based on yfinance limits
    
    Returns:
        Error message string if invalid, None if valid
    """
    # Define limits
    limits = {
        '1m': {'max_period': '7d', 'max_days': 7},
        '5m': {'max_period': '60d', 'max_days': 60},
        '15m': {'max_period': '60d', 'max_days': 60},
        '30m': {'max_period': '60d', 'max_days': 60},
        '1h': {'max_period': '730d', 'max_days': 730},
        '1d': {'max_period': None, 'max_days': None}
    }
    
    # Period to days conversion
    period_days = {
        '1d': 1, '5d': 5, '7d': 7, '1mo': 30, '3mo': 90, 
        '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
    }
    
    limit = limits.get(interval)
    if not limit:
        return None  # No limit
    
    max_days = limit['max_days']
    if max_days is None:
        return None  # No limit
    
    requested_days = period_days.get(period, 0)
    
    if requested_days > max_days:
        return f"For {interval} interval, maximum period is {limit['max_period']}. Please select a shorter period."
    
    return None



if __name__ == '__main__':
    app.run(debug=True, port=5000)

