# strategy.py - Centralized strategy configuration
class TradingStrategy:
    """
    Centralized strategy configuration
    Used across screener, backtester, and live monitoring
    """
    
    def __init__(self, name="My Strategy"):
        self.name = name
        self.selected_indicators = {
            'rsi': True,
            'macd': True,
            'bollinger': True,
            'stochastic': True,
            'adx': True,
            'volume': True,
            'cci': True,
            'willr': True,
            'mfi': True
        }
    
    def set_indicators(self, indicators_dict):
        """Update which indicators to use"""
        self.selected_indicators = indicators_dict
    
    def get_active_indicators(self):
        """Get list of active indicator names"""
        return [k for k, v in self.selected_indicators.items() if v]
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'name': self.name,
            'indicators': self.selected_indicators,
            'active_count': sum(self.selected_indicators.values())
        }

# Global strategy instance (shared across app)
current_strategy = TradingStrategy()
