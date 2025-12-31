# 📊 Stock Screener & Backtester

A professional-grade technical analysis platform for Indian stocks with real-time screening and strategy backtesting powered by yfinance.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ Features

### 📈 Stock Screener
- **Real-time screening** of multiple stocks simultaneously
- **9 Technical Indicators**: RSI, MACD, Bollinger Bands, Stochastic, ADX, Volume, CCI, Williams %R, MFI
- **Multiple Timeframes**: 1m, 5m, 15m, 30m, 1h, 1d
- **Smart Signals**: BUY/SELL/HOLD with confidence scoring
- **CSV Export**: Download screening results for analysis

### 🎯 Strategy Backtester
- **LONG & SHORT positions** with automated SL/TP
- **Risk Management**: Position sizing based on % risk per trade
- **Performance Metrics**: Win rate, drawdown, profit factor, Sharpe ratio
- **Trade Log**: Detailed entry/exit records with reasons
- **Equity Curve**: Visual portfolio growth tracking
- **CSV Upload**: Test custom historical data

### 🛠️ Technical Stack
- **Backend**: Flask (Python)
- **Data Source**: yfinance (Yahoo Finance API)
- **Indicators**: NumPy/Pandas-based calculations (no external TA libraries)
- **Frontend**: Vanilla JavaScript + CSS

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone/Download the repository**

2. Install dependencies
```
pip install -r requirements.txt
```

3. Run the application
```
python app.py
```
4. Open localhost URL in browser
```
http://localhost:5000
```

---


## 📁 Project Structure  
```
stock-screener-backtester/
│
├── app.py                 # Flask backend (API endpoints)
├── screener.py            # Stock screening logic + yfinance integration
├── backtester.py          # Backtesting engine (LONG/SHORT positions)
├── strategy.py            # Centralized strategy configuration
│
├── templates/
│   └── index.html         # Main UI
│
├── static/
│   ├── script.js          # Frontend logic
│   └── style.css          # Styling
│
├── requirements.txt       # Python dependencies
└── README.md             # Documentation
```

---

## 🎮 Usage Guide
### Stock Screener
- Select Indicators: Check boxes for indicators you want to use (minimum 1)  
- Choose Timeframe: Select from 1m to 1d intervals  
- Add Stocks: Default list includes NIFTY 50 stocks, or add custom symbols  
- Run Screener: Click "Run Stock Screener"  
- View Results: See BUY/SELL signals with confidence percentages  
- Export: Download results as CSV  


### Strategy Backtester
- Select Indicators: Check boxes for indicators you want to use (minimum 1)  
- You can change deafault parameters as per your need.  

- Run Backtest: View detailed performance metrics  
- Export Trades: Download trade log as CSV

---

## 🐛 Troubleshooting
### Issue: "Module not found: screener"
- Fix: Ensure screener.py is in the same folder as app.py

### Issue: "No data available for symbol"
- Fix:
Check stock symbol format (NSE stocks: RELIANCE.NS)  
Use 1d interval for long periods (yfinance limits intraday data)  
Try a different period (some stocks have limited history)  

### Issue: "Need at least 60 candles"
- Fix: Increase the period (e.g., 1mo → 6mo) to get more data points

### Issue: Port 5000 already in use
- Fix: Change port to 3000 or any free port - Bottom-most line of code in `app.py`

---

