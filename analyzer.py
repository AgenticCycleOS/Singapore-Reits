import pandas as pd
import numpy as np

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else 50

def calculate_sma(prices, period):
    """Calculate Simple Moving Average."""
    return prices.rolling(window=period).mean()

def analyze_reit(hist_data):
    """
    Analyze REIT data and return metrics.
    """
    if hist_data is None or hist_data.empty:
        return {
            'change_pct': 0,
            'rsi': 50,
            'trend': 'Neutral',
            'insights': ['No data available']
        }
    
    close_prices = hist_data['Close']
    
    # Calculate change percentage (week-over-week or available period)
    if len(close_prices) >= 5:
        week_ago_price = close_prices.iloc[-5]
        current_price = close_prices.iloc[-1]
        change_pct = round(((current_price - week_ago_price) / week_ago_price) * 100, 2)
    else:
        change_pct = 0
    
    # Calculate RSI
    rsi = round(calculate_rsi(close_prices), 1)
    
    # Calculate SMAs for trend
    sma_20 = calculate_sma(close_prices, 20)
    sma_50 = calculate_sma(close_prices, 50)
    
    current_price = close_prices.iloc[-1]
    sma_20_value = sma_20.iloc[-1] if len(sma_20) > 0 and not pd.isna(sma_20.iloc[-1]) else current_price
    sma_50_value = sma_50.iloc[-1] if len(sma_50) > 0 and not pd.isna(sma_50.iloc[-1]) else current_price
    
    # Determine trend
    if current_price > sma_20_value and current_price > sma_50_value:
        trend = 'Bullish'
    elif current_price < sma_20_value and current_price < sma_50_value:
        trend = 'Bearish'
    else:
        trend = 'Neutral'
    
    # Generate insights
    insights = []
    
    # RSI insights
    if rsi > 70:
        insights.append('Overbought (RSI > 70) - Overvaluation Risk')
    elif rsi < 30:
        insights.append('Oversold (RSI < 30) - Potential Value')
    else:
        insights.append('Trading within normal range')
    
    # Trend insights
    if trend == 'Bullish':
        insights.append('Strong Uptrend (Above 20 & 50 SMA)')
    elif trend == 'Bearish':
        insights.append('Downtrend (Below 20 & 50 SMA)')
    
    # Momentum insight
    if len(close_prices) >= 20:
        monthly_change = ((current_price - close_prices.iloc[-20]) / close_prices.iloc[-20]) * 100
        if monthly_change > 5:
            insights.append(f'Strong momentum (+{round(monthly_change, 1)}% monthly)')
        elif monthly_change < -5:
            insights.append(f'Weak momentum ({round(monthly_change, 1)}% monthly)')
    
    return {
        'change_pct': change_pct,
        'rsi': rsi,
        'trend': trend,
        'insights': insights
    }
