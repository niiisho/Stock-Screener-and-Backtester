// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Highlight active button
    event.target.classList.add('active');
}

// Run screener with 9 indicators
async function runScreener() {
    // Get selected indicators
    const indicators = {
        rsi: document.getElementById('ind-rsi').checked,
        macd: document.getElementById('ind-macd').checked,
        bollinger: document.getElementById('ind-bollinger').checked,
        stochastic: document.getElementById('ind-stochastic').checked,
        adx: document.getElementById('ind-adx').checked,
        volume: document.getElementById('ind-volume').checked,
        cci: document.getElementById('ind-cci').checked,
        willr: document.getElementById('ind-willr').checked,
        mfi: document.getElementById('ind-mfi').checked
    };

    // Get selected timeframe
    const timeframe = document.getElementById('screener-timeframe').value;

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('screener-results').style.display = 'none';

    try {
        const response = await fetch('/api/screen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                indicators: indicators,
                timeframe: timeframe  // NEW: Pass timeframe
            })
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.results);
            updateTime();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error running screener: ' + error);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}



let currentResults = [];


function displayResults(results) {
    const container = document.getElementById('results-container');
    container.innerHTML = '';
    currentResults = results;
    document.getElementById('export-btn').style.display = 'inline-block';
    
    // Summary
    const summary = document.createElement('div');
    summary.style.cssText = 'background: #0f172a; padding: 20px; border-radius: 8px; margin-bottom: 20px;';
    
    const buys = results.filter(s => s.signal === 'BUY').length;
    const sells = results.filter(s => s.signal === 'SELL').length;
    const holds = results.filter(s => s.signal === 'HOLD').length;
    
    summary.innerHTML = `
        <h3 style="color: #e2e8f0; margin-bottom: 15px;">Screening Summary</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
            <div style="background: #2aaf5fff; padding: 15px; border-radius: 6px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #9df8beff;">${buys}</div>
                <div style="color: #bbf7d0; margin-top: 5px;">BUY Signals</div>
            </div>
            <div style="background: #d83434ff; padding: 15px; border-radius: 6px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #e9a9a9ff;">${sells}</div>
                <div style="color: #fecaca; margin-top: 5px;">SELL Signals</div>
            </div>
            <div style="background: #2e5ee2ff; padding: 15px; border-radius: 6px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #a8cefaff;">${holds}</div>
                <div style="color: #bfdbfe; margin-top: 5px;">HOLD Signals</div>
            </div>
        </div>
    `;
    container.appendChild(summary);
    
    // Stock cards
    const stockGrid = document.createElement('div');
    stockGrid.className = 'stock-grid';
    
    results.forEach(stock => {
        const card = document.createElement('div');
        card.className = 'stock-card';
        
        // Signal color
        let signalColor, signalBg, signalEmoji;
        if (stock.signal === 'BUY') {
            signalColor = '#86efac';
            signalBg = '#14532d';
            signalEmoji = '🟢';
        } else if (stock.signal === 'SELL') {
            signalColor = '#fca5a5';
            signalBg = '#7f1d1d';
            signalEmoji = '🔴';
        } else {
            signalColor = '#93c5fd';
            signalBg = '#1e3a8a';
            signalEmoji = '🟡';
        }
        
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <h3 style="color: #e2e8f0; margin: 0; font-size: 1.3rem;">${stock.symbol}</h3>
                    <p style="color: #94a3b8; margin: 5px 0 0 0;">₹${stock.price}</p>
                </div>
                <div style="background: ${signalBg}; padding: 8px 16px; border-radius: 6px;">
                    <span style="color: ${signalColor}; font-weight: bold; font-size: 1.1rem;">
                        ${signalEmoji} ${stock.signal}
                    </span>
                </div>
            </div>
            
            <div style="background: #0f172a; padding: 12px; border-radius: 6px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #94a3b8; font-size: 0.9rem;">Confidence:</span>
                    <span style="color: #e2e8f0; font-weight: bold;">${stock.confidence}%</span>
                </div>
                <div style="background: #1e293b; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: ${signalColor}; height: 100%; width: ${stock.confidence}%;"></div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px;">
                <div style="text-align: center; padding: 8px; background: #14532d; border-radius: 4px;">
                    <div style="font-size: 1.2rem; font-weight: bold; color: #86efac;">${stock.buy_signals}</div>
                    <div style="font-size: 0.75rem; color: #bbf7d0;">BUY</div>
                </div>
                <div style="text-align: center; padding: 8px; background: #7f1d1d; border-radius: 4px;">
                    <div style="font-size: 1.2rem; font-weight: bold; color: #fca5a5;">${stock.sell_signals}</div>
                    <div style="font-size: 0.75rem; color: #fecaca;">SELL</div>
                </div>
                <div style="text-align: center; padding: 8px; background: #1e3a8a; border-radius: 4px;">
                    <div style="font-size: 1.2rem; font-weight: bold; color: #93c5fd;">${stock.neutral_signals}</div>
                    <div style="font-size: 0.75rem; color: #bfdbfe;">HOLD</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-size: 0.85rem;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #94a3b8;">RSI:</span>
                    <span style="color: #e2e8f0;">${stock.rsi}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #94a3b8;">ADX:</span>
                    <span style="color: #e2e8f0;">${stock.adx}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #94a3b8;">CCI:</span>
                    <span style="color: #e2e8f0;">${stock.cci}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #94a3b8;">MFI:</span>
                    <span style="color: #e2e8f0;">${stock.mfi}</span>
                </div>
            </div>
        `;
        
        stockGrid.appendChild(card);
    });
    
    container.appendChild(stockGrid);
    document.getElementById('screener-results').style.display = 'block';
}


async function exportToCSV() {
    if (currentResults.length === 0) {
        alert('No results to export. Please run the screener first.');
        return;
    }

    const exportBtn = document.getElementById('export-btn');
    exportBtn.disabled = true;
    exportBtn.innerText = '📥 Exporting...';

    try {
        const response = await fetch('/api/export-csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                results: currentResults
            })
        });

        if (response.ok) {
            // Download the CSV file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `stock_screening_${new Date().getTime()}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Show success message
            exportBtn.innerText = '✅ Exported!';
            setTimeout(() => {
                exportBtn.innerText = '📥 Export to CSV';
            }, 2000);
        } else {
            alert('Error exporting CSV');
            exportBtn.innerText = '📥 Export to CSV';
        }
    } catch (error) {
        alert('Error: ' + error);
        exportBtn.innerText = '📥 Export to CSV';
    } finally {
        exportBtn.disabled = false;
    }
}

// Auto-refresh
let autoRefreshInterval = null;

function toggleAutoRefresh() {
    const isEnabled = document.getElementById('auto-refresh-toggle').checked;

    if (isEnabled) {
        runScreener();
        autoRefreshInterval = setInterval(runScreener, 180000); // 3 minutes
        updateTime();
    } else {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
    }
}

// Track indicator changes globally
function updateIndicatorCount() {
    const indicators = {
        rsi: document.getElementById('ind-rsi').checked,
        macd: document.getElementById('ind-macd').checked,
        bollinger: document.getElementById('ind-bollinger').checked,
        stochastic: document.getElementById('ind-stochastic').checked,
        adx: document.getElementById('ind-adx').checked,
        volume: document.getElementById('ind-volume').checked,
        cci: document.getElementById('ind-cci').checked,
        willr: document.getElementById('ind-willr').checked,
        mfi: document.getElementById('ind-mfi').checked
    };

    const count = Object.values(indicators).filter(v => v).length;
    document.getElementById('active-indicator-count').innerText =
        `${count} indicator${count !== 1 ? 's' : ''} selected`;

    // Update backend strategy
    fetch('/api/update-strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ indicators: indicators })
    });
}

// Attach to all toggles
document.querySelectorAll('.indicator-grid input').forEach(input => {
    input.addEventListener('change', updateIndicatorCount);
});

// Backtest function
// Timeframe limits configuration
const TIMEFRAME_LIMITS = {
    '1m': { maxPeriod: '7d', maxDays: 7, label: '1 Minute' },
    '5m': { maxPeriod: '60d', maxDays: 60, label: '5 Minutes' },
    '15m': { maxPeriod: '60d', maxDays: 60, label: '15 Minutes' },
    '30m': { maxPeriod: '60d', maxDays: 60, label: '30 Minutes' },
    '1h': { maxPeriod: '730d', maxDays: 730, label: '1 Hour' },
    '1d': { maxPeriod: null, maxDays: null, label: '1 Day' }
};

const PERIOD_OPTIONS = {
    '1d': { days: 1, label: '1 Day' },
    '5d': { days: 5, label: '5 Days' },
    '7d': { days: 7, label: '7 Days' },
    '1mo': { days: 30, label: '1 Month' },
    '3mo': { days: 90, label: '3 Months' },
    '6mo': { days: 180, label: '6 Months' },
    '1y': { days: 365, label: '1 Year' },
    '2y': { days: 730, label: '2 Years' },
    '5y': { days: 1825, label: '5 Years' }
};

// Update period options based on selected interval
function updatePeriodOptions() {
    const interval = document.getElementById('interval-select').value;
    const periodSelect = document.getElementById('period-select');
    const warningDiv = document.getElementById('timeframe-warning');
    const warningText = document.getElementById('warning-text');

    const limit = TIMEFRAME_LIMITS[interval];

    // Clear existing options
    periodSelect.innerHTML = '';

    // Add valid options
    let validOptions = [];
    for (const [key, value] of Object.entries(PERIOD_OPTIONS)) {
        if (limit.maxDays === null || value.days <= limit.maxDays) {
            validOptions.push({ key, value });
        }
    }

    // Populate dropdown
    validOptions.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option.key;
        opt.textContent = option.value.label;
        periodSelect.appendChild(opt);
    });

    // Set default selection
    if (validOptions.length > 0) {
        const defaultOption = validOptions[Math.floor(validOptions.length / 2)];
        periodSelect.value = defaultOption.key;
    }

    // Show warning message
    if (limit.maxDays !== null) {
        warningDiv.style.display = 'block';
        warningText.textContent = `⚠️ ${limit.label} interval: Maximum ${limit.maxPeriod} of data available. For longer periods, use Daily interval.`;
    } else {
        warningDiv.style.display = 'none';
    }
}

async function runBacktest() {
    const dataSource = document.querySelector('input[name="data-source"]:checked').value;

    // Collect trading parameters
    const params = {
        initial_capital: parseFloat(document.getElementById('initial-capital').value),
        risk_per_trade: parseFloat(document.getElementById('risk-per-trade').value),
        stop_loss: parseInt(document.getElementById('stop-loss').value),
        take_profit: parseInt(document.getElementById('take-profit').value),
        tick_size: parseFloat(document.getElementById('tick-size').value),
        tick_value: parseFloat(document.getElementById('tick-value').value),
        commission: parseFloat(document.getElementById('commission').value),
        slippage: parseFloat(document.getElementById('slippage').value)
    };

    let requestData = { params: params };

    if (dataSource === 'csv') {
        const fileInput = document.getElementById('csv-file');
        if (!fileInput.files[0]) {
            alert('Please select a CSV file');
            return;
        }

        const csvText = await fileInput.files[0].text();
        requestData.csv_data = csvText;
    } else {
        requestData.stock = document.getElementById('stock-select').value;
        requestData.period = document.getElementById('period-select').value;
        requestData.interval = document.getElementById('interval-select').value;
        requestData.params.interval = requestData.interval;  // Add interval to params
    }

    // Show loading
    document.getElementById('backtest-loading').style.display = 'block';
    document.getElementById('backtest-results').style.display = 'none';

    try {
        const response = await fetch('/api/backtest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        if (data.success) {
            displayBacktestResults(data);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error running backtest: ' + error);
    } finally {
        document.getElementById('backtest-loading').style.display = 'none';
    }
}


// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    updatePeriodOptions();  // Set initial options
});


function toggleDataSource() {
    const dataSource = document.querySelector('input[name="data-source"]:checked').value;

    if (dataSource === 'csv') {
        document.getElementById('auto-fetch-options').style.display = 'none';
        document.getElementById('csv-upload-options').style.display = 'block';
    } else {
        document.getElementById('auto-fetch-options').style.display = 'block';
        document.getElementById('csv-upload-options').style.display = 'none';
    }
}


function displayBacktestResults(data) {
    const metricsContainer = document.getElementById('backtest-metrics');
    const tradesContainer = document.getElementById('backtest-trades');

    window.currentBacktestResults = data;

    // Metrics
    metricsContainer.innerHTML = `
        <div class="stock-grid" style="grid-template-columns: repeat(4, 1fr);">
            <div class="metric">
                <div class="metric-label">Total Return</div>
                <div class="metric-value" style="color: ${data.total_return >= 0 ? '#22c55e' : '#ef4444'}; font-size: 1.5rem;">
                    ${data.total_return >= 0 ? '+' : ''}${data.total_return}%
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Trades</div>
                <div class="metric-value">${data.total_trades}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value" style="color: ${data.win_rate >= 50 ? '#22c55e' : '#ef4444'}">
                    ${data.win_rate}%
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Max Drawdown</div>
                <div class="metric-value" style="color: #ef4444">${data.max_drawdown}%</div>
            </div>
        </div>
        
        <div class="stock-grid" style="grid-template-columns: repeat(4, 1fr); margin-top: 15px;">
            <div class="metric">
                <div class="metric-label">Avg Profit/Trade</div>
                <div class="metric-value" style="color: ${data.avg_profit_per_trade >= 0 ? '#22c55e' : '#ef4444'}">
                    ${data.avg_profit_per_trade >= 0 ? '+' : ''}${data.avg_profit_per_trade}
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Win</div>
                <div class="metric-value" style="color: #22c55e">
                    +${data.avg_win}
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Loss</div>
                <div class="metric-value" style="color: #ef4444">
                    ${data.avg_loss}
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Final Capital</div>
                <div class="metric-value">${data.final_capital.toLocaleString()}</div>
            </div>
        </div>
        
        <div style="background: #0f172a; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color: #e2e8f0; margin-bottom: 10px;">Exit Analysis:</h4>
            <div style="display: flex; gap: 20px; color: #94a3b8;">
                <span>Stop Loss: ${data.sl_exits}</span>
                <span>Take Profit: ${data.tp_exits}</span>
                <span>Signal Exit: ${data.signal_exits}</span>
            </div>
        </div>
    `;

    // Trades Table
    if (data.trades && data.trades.length > 0) {
        tradesContainer.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: #e2e8f0; margin: 0;">Trade History (${data.trades.length} trades)</h3>
                <button class="btn-secondary" onclick="exportBacktestTrades()" style="padding: 10px 20px; font-size: 0.9rem;">
                    Download Trades CSV
                </button>
            </div>
            
            <div style="overflow-x: auto; max-height: 600px; overflow-y: auto; border: 1px solid #334155; border-radius: 8px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                    <thead style="position: sticky; top: 0; background: #1e293b; z-index: 10;">
                        <tr>
                            <th style="padding: 12px; text-align: left; color: #94a3b8; border-bottom: 2px solid #334155;">Entry Time</th>
                            <th style="padding: 12px; text-align: center; color: #94a3b8; border-bottom: 2px solid #334155;">Position</th>
                            <th style="padding: 12px; text-align: right; color: #94a3b8; border-bottom: 2px solid #334155;">Entry</th>
                            <th style="padding: 12px; text-align: right; color: #94a3b8; border-bottom: 2px solid #334155;">SL</th>
                            <th style="padding: 12px; text-align: right; color: #94a3b8; border-bottom: 2px solid #334155;">TP</th>
                            <th style="padding: 12px; text-align: left; color: #94a3b8; border-bottom: 2px solid #334155;">Exit Time</th>
                            <th style="padding: 12px; text-align: right; color: #94a3b8; border-bottom: 2px solid #334155;">Exit</th>
                            <th style="padding: 12px; text-align: center; color: #94a3b8; border-bottom: 2px solid #334155;">Reason</th>
                            <th style="padding: 12px; text-align: right; color: #94a3b8; border-bottom: 2px solid #334155;">P&L</th>
                            <th style="padding: 12px; text-align: right; color: #94a3b8; border-bottom: 2px solid #334155;">Cumulative P&L</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.trades.map((trade, index) => `
                            <tr style="border-bottom: 1px solid #334155; background: ${index % 2 === 0 ? '#0f172a' : '#1e293b'};">
                                <td style="padding: 12px; color: #e2e8f0;">${formatTradeDate(trade.entry_time)}</td>
                                <td style="padding: 12px; text-align: center;">
                                    <span style="padding: 4px 12px; border-radius: 4px; background: ${trade.position === 'long' ? '#14532d' : '#7f1d1d'}; color: ${trade.position === 'long' ? '#86efac' : '#fca5a5'}; text-transform: uppercase; font-weight: bold;">
                                        ${trade.position}
                                    </span>
                                </td>
                                <td style="padding: 12px; text-align: right; color: #e2e8f0; font-family: monospace;">${trade.entry}</td>
                                <td style="padding: 12px; text-align: right; color: #94a3b8; font-family: monospace;">${trade.sl}</td>
                                <td style="padding: 12px; text-align: right; color: #94a3b8; font-family: monospace;">${trade.tp}</td>
                                <td style="padding: 12px; color: #e2e8f0;">${formatTradeDate(trade.exit_time)}</td>
                                <td style="padding: 12px; text-align: right; color: #e2e8f0; font-family: monospace;">${trade.exit}</td>
                                <td style="padding: 12px; text-align: center;">
                                    <span style="padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; background: ${getReasonBg(trade.reason)}; color: ${getReasonColor(trade.reason)};">
                                        ${trade.reason}
                                    </span>
                                </td>
                                <td style="padding: 12px; text-align: right; font-weight: bold; font-family: monospace; color: ${trade.pnl >= 0 ? '#22c55e' : '#ef4444'};">
                                    ${trade.pnl >= 0 ? '+' : ''}${trade.pnl}
                                </td>
                                <td style="padding: 12px; text-align: right; font-weight: bold; font-family: monospace; color: ${trade.cumulative_pnl >= 0 ? '#22c55e' : '#ef4444'};">
                                    ${trade.cumulative_pnl >= 0 ? '+' : ''}${trade.cumulative_pnl}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 10px; text-align: center;">
                Showing 1-${data.trades.length} of ${data.trades.length}
            </p>
        `;
    } else {
        tradesContainer.innerHTML = `
            <p style="color: #94a3b8; text-align: center; padding: 40px;">No trades executed. Try adjusting parameters.</p>
        `;
    }

    document.getElementById('backtest-results').style.display = 'block';
}

function formatTradeDate(dateStr) {
    const date = new Date(dateStr);
    if (isNaN(date)) return dateStr;
    return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

function getReasonBg(reason) {
    const colors = {
        'SL': '#7f1d1d',
        'TP': '#14532d',
        'Signal': '#1e3a8a'
    };
    return colors[reason] || '#1e293b';
}

function getReasonColor(reason) {
    const colors = {
        'SL': '#fca5a5',
        'TP': '#86efac',
        'Signal': '#93c5fd'
    };
    return colors[reason] || '#94a3b8';
}

function exportBacktestTrades() {
    if (!window.currentBacktestResults || !window.currentBacktestResults.trades) {
        alert('No trades to export');
        return;
    }

    const trades = window.currentBacktestResults.trades;

    let csvContent = 'Entry Time,Position,Entry,SL,TP,Exit Time,Exit,Reason,P&L,Cumulative P&L\n';

    trades.forEach(trade => {
        csvContent += `${trade.entry_time},${trade.position},${trade.entry},${trade.sl},${trade.tp},${trade.exit_time},${trade.exit},${trade.reason},${trade.pnl},${trade.cumulative_pnl}\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `backtest_trades_${new Date().getTime()}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}






function updateTime() {
    const now = new Date().toLocaleTimeString('en-IN');
    document.getElementById('last-updated').innerText = `Last updated: ${now}`;
}


// Helper function for signal emojis
function getSignalEmoji(signal) {
    const emojis = {
        'STRONG BUY': '🟢🟢',
        'BUY': '🟢',
        'HOLD': '🟡',
        'SELL': '🔴',
        'STRONG SELL': '🔴🔴'
    };
    return emojis[signal] || '⚪';
}
